Development notes
=================

Quick tests
-----------

- Import smoke test:

```powershell
python -c "from application.app import app; print('App created successfully')"
```

- Database integration test (create/list):

```powershell
python - <<'PY'
from application.services.annotations_service import AnnotationsService
from pathlib import Path
PROJECT_ROOT = Path('.')
service = AnnotationsService(PROJECT_ROOT, use_db=True)
print('service.use_db =', service.use_db)
ann = service.create('2024-01-01', 'SE3', 'Dev test', 'dev')
print('created:', ann)
print('found:', service.list('2024-01-01', 'SE3'))
PY
```

Notes about SQLAlchemy compatibility
-----------------------------------

- If you run Python 3.13+, older SQLAlchemy versions (e.g., 2.0.22) may raise typing/AssertionError errors when importing.
- Upgrade SQLAlchemy to the latest 2.x release if you see such errors:

```powershell
pip install --upgrade SQLAlchemy
```

Tips for debugging database vs JSON usage
----------------------------------------

- The service will prefer the DB when both SQLAlchemy is installed and the models file initializes the DB successfully.
- To verify which backend is active, create an `AnnotationsService` with `use_db=True` and check `service.use_db`.
- If `service.use_db` is False but you expect DB usage:
  - Confirm `annotations.db` exists in project root
  - Confirm `requirements.txt` contains `SQLAlchemy` and it's installed in your venv
  - Run the import smoke test from project root

Additional developer notes
--------------------------

- The project uses class-based views in `application/endpoints.py` and a service layer in `application/services/annotations_service.py`.
- If you need a migration tool to move JSON annotations into the DB, I can add a safe migration script that checks for duplicates.
- Tests: there are no unit tests in the repo currently; adding a small pytest suite for the annotations service would be a good next step.

Continuous Integration
----------------------

A GitHub Actions workflow is added at `.github/workflows/pytest.yml` that runs `pytest` on push and pull requests against `main` on multiple Python versions (3.10–3.12).

To run tests locally before pushing, use PowerShell from the project root:

```powershell
.\.venv\Scripts\Activate.ps1
pytest -q
```

If you see SQLAlchemy typing/deprecation warnings, upgrade SQLAlchemy in your venv:

```powershell
pip install --upgrade SQLAlchemy
```
