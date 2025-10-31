from pathlib import Path
import json
from datetime import datetime, date
from typing import Any, Optional


def project_root() -> Path:
    """Return the project root (parent of this file's parent)."""
    return Path(__file__).resolve().parents[1]


def read_json(path: Path) -> Optional[Any]:
    try:
        with path.open('r', encoding='utf-8') as fh:
            return json.load(fh)
    except Exception:
        return None


def write_json(path: Path, data: Any) -> bool:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w', encoding='utf-8') as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def today_iso() -> str:
    return date.today().isoformat()


def parse_iso_date(s: str) -> Optional[date]:
    try:
        return datetime.fromisoformat(s).date()
    except Exception:
        return None


def db_path() -> Path:
    return project_root() / 'annotations.db'
