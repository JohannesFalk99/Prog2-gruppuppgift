from pathlib import Path
import json
import uuid
from datetime import datetime

# Try to import DB models
USE_SQLALCHEMY = False
try:
    from ..models import Annotation, get_session
    USE_SQLALCHEMY = True
except ImportError as e:
    pass

class AnnotationsService:
    """Service responsible for annotations persistence.

    Supports both JSON-file and SQLite backends. Uses SQLite if available and configured.
    """

    def __init__(self, project_root: Path, use_db: bool = False):
        self.project_root = project_root
        self.path = project_root / 'annotations.json'
        self.use_db = use_db and USE_SQLALCHEMY

    def _load(self):
        """Load from JSON file (fallback only)"""
        if not self.path.exists():
            return []
        try:
            with self.path.open('r', encoding='utf-8') as fh:
                data = json.load(fh)
                return data if isinstance(data, list) else []
        except Exception:
            return []

    def _save(self, items):
        """Save to JSON file (fallback only)"""
        try:
            with self.path.open('w', encoding='utf-8') as fh:
                json.dump(items, fh, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def list(self, date=None, area=None):
        """List annotations with optional filters"""
        if self.use_db:
            try:
                sess = get_session()
                q = sess.query(Annotation)
                if date:
                    q = q.filter(Annotation.date == date)
                if area:
                    q = q.filter(Annotation.area == area)
                rows = q.all()
                return [{
                    'id': r.id,
                    'date': r.date,
                    'area': r.area,
                    'text': r.text,
                    'author': r.author,
                    'created_at': r.created_at.isoformat() if r.created_at else None,
                    'likes': r.likes,
                    'dislikes': r.dislikes,
                    'status': r.status,
                } for r in rows]
            except Exception:
                # Fallback to JSON if DB fails
                items = self._load()
                if date:
                    items = [a for a in items if a.get('date') == date]
                if area:
                    items = [a for a in items if a.get('area') == area]
                return items
        else:
            items = self._load()
            if date:
                items = [a for a in items if a.get('date') == date]
            if area:
                items = [a for a in items if a.get('area') == area]
            return items

    def create(self, date, area, text, author='anonymous', hour=None):
        """Create a new annotation"""
        ann_id = str(uuid.uuid4())
        created_at = datetime.utcnow()
        
        if self.use_db:
            try:
                sess = get_session()
                a = Annotation(
                    id=ann_id,
                    date=date,
                    area=area,
                    text=text,
                    author=author,
                    likes=0,
                    dislikes=0,
                    status='active'
                )
                sess.add(a)
                sess.commit()
                return {
                    'id': a.id,
                    'date': a.date,
                    'area': a.area,
                    'text': a.text,
                    'author': a.author,
                    'created_at': a.created_at.isoformat() if a.created_at else None,
                    'likes': a.likes,
                    'dislikes': a.dislikes,
                    'status': a.status,
                }
            except Exception:
                # Fallback to JSON
                pass
        
        # JSON fallback
        ann = {
            'id': ann_id,
            'date': date,
            'area': area,
            'text': text,
            'author': author,
            'hour': hour,
            'created_at': created_at.isoformat() + 'Z',
            'likes': 0,
            'dislikes': 0,
            'status': 'active'
        }
        items = self._load()
        items.append(ann)
        self._save(items)
        return ann

    def vote(self, ann_id, vote):
        """Vote on an annotation"""
        if self.use_db:
            try:
                sess = get_session()
                a = sess.query(Annotation).filter(Annotation.id == ann_id).one_or_none()
                if not a:
                    return None
                if vote == 'like':
                    a.likes += 1
                else:
                    a.dislikes += 1
                d = a.dislikes
                if d >= 5:
                    a.status = 'removed'
                elif d >= 3:
                    a.status = 'warning'
                else:
                    if a.status in ('warning', 'removed') and d < 3:
                        a.status = 'active'
                sess.commit()
                return {
                    'id': a.id,
                    'date': a.date,
                    'area': a.area,
                    'text': a.text,
                    'author': a.author,
                    'created_at': a.created_at.isoformat() if a.created_at else None,
                    'likes': a.likes,
                    'dislikes': a.dislikes,
                    'status': a.status,
                }
            except Exception:
                # Fallback to JSON
                pass
        
        # JSON fallback
        items = self._load()
        found = None
        for a in items:
            if a.get('id') == ann_id:
                found = a
                break
        if not found:
            return None
        if vote == 'like':
            found['likes'] = int(found.get('likes', 0)) + 1
        else:
            found['dislikes'] = int(found.get('dislikes', 0)) + 1
        d = int(found.get('dislikes', 0))
        if d >= 5:
            found['status'] = 'removed'
        elif d >= 3:
            found['status'] = 'warning'
        else:
            if found.get('status') in ('warning', 'removed') and d < 3:
                found['status'] = 'active'
        self._save(items)
        return found

    def moderate(self, ann_id, action):
        """Moderate an annotation"""
        if self.use_db:
            try:
                sess = get_session()
                a = sess.query(Annotation).filter(Annotation.id == ann_id).one_or_none()
                if not a:
                    return None
                if action == 'remove':
                    a.status = 'removed'
                elif action == 'warn':
                    a.status = 'warning'
                else:
                    a.status = 'active'
                sess.commit()
                return {
                    'id': a.id,
                    'date': a.date,
                    'area': a.area,
                    'text': a.text,
                    'author': a.author,
                    'created_at': a.created_at.isoformat() if a.created_at else None,
                    'likes': a.likes,
                    'dislikes': a.dislikes,
                    'status': a.status,
                }
            except Exception:
                # Fallback to JSON
                pass
        
        # JSON fallback
        items = self._load()
        found = None
        for a in items:
            if a.get('id') == ann_id:
                found = a
                break
        if not found:
            return None
        if action == 'remove':
            found['status'] = 'removed'
        elif action == 'warn':
            found['status'] = 'warning'
        else:
            found['status'] = 'active'
        self._save(items)
        return found
