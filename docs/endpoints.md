Endpoints reference
===================

This file lists the main routes in the app and their parameters.

Views / Pages
-------------

- `/` — Home page (template `index.html`). Shows cookie consent state and user id.
- `/elpriser` — View for electricity prices. Query params: `year`, `month`, `day`, `prisklass` (or `area`). If missing, defaults to today and `SE3`.
- `/pandas` — Pandas demo page (generates a chart).
- `/data`, `/profile`, `/dashboard`, `/settings` — Misc pages (render templates).

Elpriser API
------------

- `POST /fetch_elpriser` or `GET /fetch_elpriser`
  - Body or query params: `year`, `month`, `day`, `prisklass` (one of `SE1`, `SE2`, `SE3`, `SE4`)
  - Response: JSON with `labels`, `values`, `summary` on success.
  - Debug flag: `?debug=1` returns persisted raw payload.

Persisted elpriser payload
--------------------------
- `GET /elpriser_data.json` — serves the persisted `elpriser_data.json` stored in the project root.

Annotations API
---------------

- `GET /annotations` — list annotations
  - Query params:
    - `date` (YYYY-MM-DD) or `year`/`month`/`day` triple
    - `prisklass` or `area`
  - Response: `{ "annotations": [ ... ] }`

- `POST /annotations` — create annotation
  - Body JSON: `{ "text": "...", "date": "YYYY-MM-DD", "area": "SE3", "author": "optional" }`
  - Response: `{ "annotation": { ... } }` (201 on success)

- `POST /annotations/<ann_id>/vote` — vote on an annotation
  - Body JSON: `{ "vote": "like" | "dislike" }`
  - Response: updated annotation object

- `PUT /annotations/<ann_id>/moderate` — moderate annotation
  - Body JSON: `{ "action": "remove" | "warn" | "restore" }`
  - Response: updated annotation object

Notes
-----
- Many routes are implemented via class-based views in `application/endpoints.py`.
- The annotations endpoints use `application/services/annotations_service.py` for persistence and accept date+area filters as query params.
