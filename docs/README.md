Prog2-gruppuppgift
====================

Small Flask project for displaying electricity prices and allowing user annotations.

Docs index

- README.md — this file
- setup.md — how to set up the development environment and run the app
- annotations.md — how annotations are stored and how the SQLite/JSON fallback works
- endpoints.md — API and view endpoints with parameters
- development.md — developer notes, testing and debugging tips

Project structure (top-level):

- `application/` — Flask application package
- `static/` — static assets (css, js)
- `templates/` — Jinja2 templates
- `annotations.db` — SQLite DB containing annotations (created when DB is used)
- `annotations.json` — legacy JSON fallback for annotations
- `requirements.txt` — pinned Python dependencies

Quick start (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -c "from application.app import app; print('App created successfully')"
```

See `setup.md` for detailed setup instructions.
