Setup and Run (Windows / PowerShell)
====================================

1) Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Install dependencies

```powershell
pip install -r requirements.txt
```

Note: If you are running Python 3.13+ and see SQLAlchemy errors, upgrade SQLAlchemy:

```powershell
pip install --upgrade SQLAlchemy
```

3) Quick smoke test (import app only)

```powershell
python -c "from application.app import app; print('App created successfully')"
```

4) Run the Flask app locally

```powershell
python -c "from application.app import FlaskApp; FlaskApp().run()"
```

5) Inspect the annotations database

- The SQLite DB file is `annotations.db` in the project root.
- You can open it with DB Browser for SQLite or using the `sqlite3` CLI.

Example using sqlite3 (PowerShell):

```powershell
sqlite3.exe annotations.db
sqlite> .tables
sqlite> SELECT id, date, area, text FROM annotations LIMIT 10;
```

If the DB is not used, the app will fall back to `annotations.json` in the project root.
