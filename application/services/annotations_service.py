from pathlib import Path
import json
import uuid
from datetime import datetime


class AnnotationsService:
    """Service responsible for annotations persistence.

    Uses a JSON-file backend by default. The service exposes simple methods so
    endpoints can switch to a DB-backed implementation later without changing
    the route handlers.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.path = project_root / 'annotations.json'

    def _load(self):
        if not self.path.exists():
            return []
        try:
            with self.path.open('r', encoding='utf-8') as fh:
                data = json.load(fh)
                return data if isinstance(data, list) else []
        except Exception:
            return []

    def _save(self, items):
        try:
            with self.path.open('w', encoding='utf-8') as fh:
                json.dump(items, fh, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def list(self, date=None, area=None):
        items = self._load()
        if date:
            items = [a for a in items if a.get('date') == date]
        if area:
            items = [a for a in items if a.get('area') == area]
        return items

    def create(self, date, area, text, author='anonymous', hour=None):
        ann = {
            'id': str(uuid.uuid4()),
            'date': date,
            'area': area,
            'text': text,
            'author': author,
            'hour': hour,
            'created_at': datetime.utcnow().isoformat() + 'Z',
            'likes': 0,
            'dislikes': 0,
            'status': 'active'
        }
        items = self._load()
        items.append(ann)
        ok = self._save(items)
        return ann if ok else None

    def vote(self, ann_id, vote):
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
        ok = self._save(items)
        return found if ok else None

    def moderate(self, ann_id, action):
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
        ok = self._save(items)
        return found if ok else None
