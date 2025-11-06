Annotations storage
====================

This project supports two persistence backends for annotations:

1) SQLite (preferred)
2) JSON file fallback (`annotations.json`)

How the service chooses the backend
-----------------------------------

- At import time the code attempts to import SQLAlchemy and the `models` module.
- If SQLAlchemy is available and `models.init_db()` succeeds, the project sets `USE_DB=True` and uses SQLite.
- If SQLAlchemy is missing or database initialization fails, the application falls back to `annotations.json`.

Database path
-------------

- SQLite database file: `annotations.db` in the project root.
- SQLAlchemy models are declared in `application/models.py` and are used by `application/services/annotations_service.py`.

Inspecting the SQLite DB
------------------------

- Recommended GUI: DB Browser for SQLite (https://sqlitebrowser.org/)
- CLI example (PowerShell):

```powershell
sqlite3.exe annotations.db
# list tables
sqlite> .tables
# view schema
sqlite> .schema annotations
# view rows
sqlite> SELECT id, date, area, text, likes, dislikes, status FROM annotations ORDER BY created_at DESC LIMIT 50;
```

Notes about JSON fallback
-------------------------

- The fallback file is `annotations.json` in the project root. It contains an array of annotation objects.
- When the database is enabled, new annotations will be persisted to `annotations.db`. The JSON file remains as a historical fallback and will not be automatically removed.
- If the database is not available, all read/write operations use `annotations.json`.

How to force use of DB (for debugging)
--------------------------------------

- Ensure SQLAlchemy is installed in your environment:

```powershell
pip install SQLAlchemy
```

- Optionally upgrade SQLAlchemy if you run Python 3.13+:

```powershell
pip install --upgrade SQLAlchemy
```

- Run the import smoke test to verify DB initialization:

```powershell
python -c "from application.app import app; print('App created successfully')"
```

Troubleshooting
---------------

- If you see errors like "No module named 'services'" or import errors, run the import command from the project root and make sure `application` is treated as a package (it contains `__init__.py`).
- For SQLAlchemy assertion errors on newer Python versions, upgrading SQLAlchemy resolved the issue in this repository.

If you want a migration script to copy existing JSON annotations into the SQLite DB, I can add that next.
