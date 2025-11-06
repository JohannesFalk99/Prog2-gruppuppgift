import uuid
from flask import request, make_response, redirect, url_for, current_app
import hashlib
from pathlib import Path
from datetime import datetime

class CookieManager:
    """Manages cookie operations for the Flask application"""

    def __init__(self, consent_days=None, user_id_days=None):
        # Use config values if available, otherwise defaults
        try:
            from flask import current_app
            # Default cookie lifetimes changed to 7 days for assignment
            self.consent_days = consent_days or current_app.config.get('COOKIE_CONSENT_DAYS', 7)
            self.user_id_days = user_id_days or current_app.config.get('COOKIE_USER_ID_DAYS', 7)
        except RuntimeError:
            # Outside of app context
            self.consent_days = consent_days or 7
            self.user_id_days = user_id_days or 7

    def _set_cookie(self, response, key, value, days_expire=None):
        """Set a cookie with proper security settings"""
        if days_expire is None:
            days_expire = self.consent_days
        max_age = days_expire * 24 * 60 * 60
        response.set_cookie(key, value, max_age=max_age, httponly=True, samesite="Lax")
        return response

    def get_cookie(self, key):
        """Get a cookie value"""
        return request.cookies.get(key)

    def delete_cookie(self, response, key):
        """Delete a cookie"""
        response.delete_cookie(key)
        return response

    def has_consent(self):
        """Check if user has given cookie consent"""
        return self.get_cookie("consent") == "true"

    def get_user_id(self):
        """Get the user's ID from cookies"""
        return self.get_cookie("user_id")

    def accept_cookies(self):
        """Accept cookies and set consent + user ID"""
        resp = make_response(redirect(url_for("index")))
        resp = self._set_cookie(resp, "consent", "true", self.consent_days)

        # Create user ID if it doesn't exist
        if not self.get_user_id():
            user_id = str(uuid.uuid4())
            resp = self._set_cookie(resp, "user_id", user_id, self.user_id_days)
            # attempt to persist cookie acceptance and fingerprint to DB or JSON
            try:
                from .models import CookieRecord, get_session
                ua = request.headers.get('User-Agent')
                al = request.headers.get('Accept-Language')
                # lightweight fingerprint: hash of user-agent + accept-language
                fp_src = (ua or '') + '|' + (al or '')
                fp_hash = hashlib.sha256(fp_src.encode('utf-8')).hexdigest()
                sess = get_session()
                cr = CookieRecord(id=str(uuid.uuid4()), user_id=user_id, user_agent=ua, accept_language=al, fingerprint_hash=fp_hash, views=0, annotations_count=0, created_at=datetime.utcnow(), last_seen=datetime.utcnow())
                sess.add(cr)
                sess.commit()
            except Exception:
                # DB not available, try JSON fallback
                try:
                    self._save_cookie_record_to_json(user_id, request.headers.get('User-Agent'), 
                                                   request.headers.get('Accept-Language'))
                except Exception:
                    current_app.logger.debug('CookieManager: Neither DB nor JSON fallback worked')
                    pass

        return resp

    def decline_cookies(self):
        """Decline cookies by setting consent to false"""
        resp = make_response(redirect(url_for("index")))
        return self._set_cookie(resp, "consent", "false", self.consent_days)

    def record_view(self):
        """Record a page view for the current user_id in the DB (if available).

        This will increment `views` and update `last_seen` for the CookieRecord
        associated with the current `user_id` cookie.
        """
        try:
            uid = self.get_user_id()
            if not uid:
                return
            from .models import CookieRecord, get_session
            sess = get_session()
            cr = sess.query(CookieRecord).filter(CookieRecord.user_id == uid).one_or_none()
            if cr:
                # tolerate None values
                cr.views = (cr.views or 0) + 1
                cr.last_seen = datetime.utcnow()
                sess.commit()
        except Exception:
            # DB not available, try JSON fallback
            try:
                uid = self.get_user_id()
                if uid:
                    self._update_view_count_in_json(uid)
            except Exception:
                try:
                    current_app.logger.debug('CookieManager.record_view: Both DB and JSON fallback failed')
                except Exception:
                    pass
            return

    def _save_cookie_record_to_json(self, user_id, user_agent, accept_language):
        """Save cookie record to JSON file as fallback when DB is not available"""
        import json
        from pathlib import Path
        
        cookie_records_file = Path(__file__).parent.parent / "cookie_records.json"
        
        # Create new record
        fp_src = (user_agent or '') + '|' + (accept_language or '')
        fp_hash = hashlib.sha256(fp_src.encode('utf-8')).hexdigest()
        
        new_record = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'user_agent': user_agent,
            'accept_language': accept_language,
            'fingerprint_hash': fp_hash,
            'created_at': datetime.utcnow().isoformat(),
            'last_seen': datetime.utcnow().isoformat(),
            'views': 1,
            'annotations_count': 0
        }
        
        # Load existing records
        try:
            with open(cookie_records_file, 'r', encoding='utf-8') as f:
                records = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            records = []
        
        # Add new record
        records.append(new_record)
        
        # Save back to file
        with open(cookie_records_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=2, ensure_ascii=False)

    def _update_view_count_in_json(self, user_id):
        """Update view count in JSON file"""
        import json
        from pathlib import Path
        
        cookie_records_file = Path(__file__).parent.parent / "cookie_records.json"
        
        try:
            # Load existing records
            with open(cookie_records_file, 'r', encoding='utf-8') as f:
                records = json.load(f)
            
            # Find and update the record
            for record in records:
                if record['user_id'] == user_id:
                    record['views'] = record.get('views', 0) + 1
                    record['last_seen'] = datetime.utcnow().isoformat()
                    break
            
            # Save back to file
            with open(cookie_records_file, 'w', encoding='utf-8') as f:
                json.dump(records, f, indent=2, ensure_ascii=False)
                
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def _update_annotation_count_in_json(self, user_id):
        """Update annotation count in JSON file"""
        import json
        from pathlib import Path
        
        cookie_records_file = Path(__file__).parent.parent / "cookie_records.json"
        
        try:
            # Load existing records
            with open(cookie_records_file, 'r', encoding='utf-8') as f:
                records = json.load(f)
            
            # Find and update the record
            for record in records:
                if record['user_id'] == user_id:
                    record['annotations_count'] = record.get('annotations_count', 0) + 1
                    record['last_seen'] = datetime.utcnow().isoformat()
                    break
            
            # Save back to file
            with open(cookie_records_file, 'w', encoding='utf-8') as f:
                json.dump(records, f, indent=2, ensure_ascii=False)
                
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def clear_cookies(self):
        """Clear all cookies and redirect to index"""
        resp = make_response(redirect(url_for("index")))
        # Delete cookies with the same parameters they were set with
        resp.set_cookie("user_id", "", expires=0, httponly=True, samesite="Lax")
        resp.set_cookie("consent", "", expires=0, httponly=True, samesite="Lax")
        return resp

    @staticmethod
    def register_routes(app):
        """Register cookie-related routes with the Flask app"""
        cookie_manager = CookieManager()

        @app.route("/accept_cookies")
        def accept_cookies_route():
            return cookie_manager.accept_cookies()

        @app.route("/decline_cookies") 
        def decline_cookies_route():
            return cookie_manager.decline_cookies()

        @app.route("/set")
        def set_cookie_route():
            return cookie_manager.accept_cookies()

        @app.route("/get")
        def get_cookie_route():
            user_id = request.cookies.get("user_id")
            return f"user_id = {user_id}" if user_id else "NO cookies claimed!"

        @app.route("/delete")
        def delete_cookie_route():
            return cookie_manager.clear_cookies()
        
        @app.route("/clear_cookies")
        def clear_cookies_route():
            return cookie_manager.clear_cookies()
        
        @app.route("/cookie_status")
        def cookie_status_route():
            consent = cookie_manager.has_consent()
            user_id = cookie_manager.get_user_id()
            status = {
                "consent": consent,
                "user_id": user_id,
                "raw_cookies": dict(request.cookies)
            }
            return f"<pre>{status}</pre><br><a href='/clear_cookies'>Clear Cookies</a><br><a href='/'>Back to Home</a><br><a href='/debug_admin'>Debug Admin Data</a>"
        
        @app.route("/debug_admin")
        def debug_admin_route():
            from pathlib import Path
            try:
                from .admin import get_admin_dashboard_data
            except ImportError:
                from admin import get_admin_dashboard_data
            
            project_root = Path(__file__).parent.parent
            
            # Test JSON file directly
            import json
            cookie_records_file = project_root / "cookie_records.json"
            json_content = "File not found"
            if cookie_records_file.exists():
                with open(cookie_records_file, 'r', encoding='utf-8') as f:
                    json_content = json.load(f)
            
            # Test admin function
            data = get_admin_dashboard_data(project_root=project_root, limit=200)
            
            result = {
                "json_file_path": str(cookie_records_file),
                "json_file_exists": cookie_records_file.exists(),
                "json_content": json_content,
                "admin_data": data
            }
            return f"<pre>Debug Info:\n{result}</pre><br><a href='/admin/login'>Admin Login</a><br><a href='/admin?password=123'>Direct Admin</a><br><a href='/test_annotation'>Test Annotation</a><br><a href='/'>Home</a>"
        
        @app.route("/test_annotation")
        def test_annotation_route():
            """Test route to create an annotation and check if counter updates"""
            from datetime import datetime
            import requests
            import json
            
            # Get current user_id
            user_id = cookie_manager.get_user_id()
            if not user_id:
                return "<h3>No user_id cookie found. Please accept cookies first!</h3><br><a href='/'>Go Home</a><br><a href='/accept_cookies'>Accept Cookies</a>"
            
            # Create a test annotation via internal API
            test_data = {
                'text': f'Test annotation created at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                'date': '2025-11-04',
                'area': 'SE3',
                'author': 'test-user'
            }
            
            # Try to create annotation via service directly
            try:
                try:
                    from .services.annotations_service import AnnotationsService
                except ImportError:
                    from services.annotations_service import AnnotationsService
                
                from pathlib import Path
                project_root = Path(__file__).parent.parent
                ann_service = AnnotationsService(project_root, use_db=False)  # Force JSON mode
                ann = ann_service.create(date=test_data['date'], area=test_data['area'], 
                                       text=test_data['text'], author=test_data['author'], 
                                       user_id=user_id)
                
                if ann:
                    # Update annotation count manually since we bypassed the API
                    try:
                        cookie_manager._update_annotation_count_in_json(user_id)
                        result = f"✅ Annotation created successfully!<br>ID: {ann.get('id', 'N/A')}<br>User ID: {user_id}"
                    except Exception as e:
                        result = f"⚠️ Annotation created but counter update failed: {e}"
                else:
                    result = "❌ Failed to create annotation"
                    
            except Exception as e:
                result = f"❌ Error creating annotation: {e}"
            
            return f"<h3>Test Annotation Result</h3><p>{result}</p><br><a href='/admin?password=123'>Check Admin Panel</a><br><a href='/create_annotation_form'>Create Annotation Form</a><br><a href='/'>Home</a>"
        
        @app.route("/create_annotation_form")
        def create_annotation_form():
            """Simple form to create annotations for testing"""
            user_id = cookie_manager.get_user_id()
            if not user_id:
                return "<h3>No cookies found!</h3><br><a href='/accept_cookies'>Accept Cookies</a><br><a href='/'>Home</a>"
            
            return f"""
            <h3>Create Test Annotation</h3>
            <p><strong>Current User ID:</strong> {user_id[:8]}...</p>
            <form method="POST" action="/create_annotation">
                <p><label>Text:</label><br>
                <textarea name="text" rows="3" cols="50">Test annotation from form at {datetime.now().strftime('%H:%M:%S')}</textarea></p>
                <p><label>Date:</label><br>
                <input type="date" name="date" value="2025-11-04"></p>
                <p><label>Area:</label><br>
                <select name="area">
                    <option value="SE1">SE1</option>
                    <option value="SE2">SE2</option>
                    <option value="SE3" selected>SE3</option>
                    <option value="SE4">SE4</option>
                </select></p>
                <p><label>Author:</label><br>
                <input type="text" name="author" value="Test User"></p>
                <p><button type="submit">Create Annotation</button></p>
            </form>
            <br><a href='/admin?password=123'>Admin Panel</a> | <a href='/'>Home</a>
            """
        
        @app.route("/create_annotation", methods=["POST"])
        def create_annotation():
            """Handle annotation creation from form"""
            from flask import request
            
            user_id = cookie_manager.get_user_id() 
            if not user_id:
                return "<h3>Error: No user_id cookie!</h3><br><a href='/'>Home</a>"
            
            text = request.form.get('text')
            date = request.form.get('date') 
            area = request.form.get('area')
            author = request.form.get('author', 'anonymous')
            
            if not all([text, date, area]):
                return f"<h3>Error: Missing fields!</h3><p>Text: {text}<br>Date: {date}<br>Area: {area}</p><br><a href='/create_annotation_form'>Back</a>"
            
            # Create annotation via service
            try:
                try:
                    from .services.annotations_service import AnnotationsService
                except ImportError:
                    from services.annotations_service import AnnotationsService
                
                from pathlib import Path
                project_root = Path(__file__).parent.parent
                ann_service = AnnotationsService(project_root, use_db=False)
                
                ann = ann_service.create(date=date, area=area, text=text, author=author, user_id=user_id)
                
                if ann:
                    # Update annotation count
                    cookie_manager._update_annotation_count_in_json(user_id)
                    return f"""
                    <h3>✅ Success!</h3>
                    <p><strong>Annotation created:</strong><br>
                    ID: {ann.get('id', 'N/A')}<br>
                    Text: {text}<br>
                    Date: {date}<br>
                    Area: {area}<br>
                    User ID: {user_id[:8]}...</p>
                    <br><a href='/admin?password=123'>Check Admin Panel</a> | <a href='/create_annotation_form'>Create Another</a> | <a href='/'>Home</a>
                    """
                else:
                    return f"<h3>❌ Failed to create annotation</h3><br><a href='/create_annotation_form'>Try Again</a>"
                    
            except Exception as e:
                return f"<h3>❌ Error: {e}</h3><br><a href='/create_annotation_form'>Try Again</a>"
