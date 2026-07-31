# Udatracker Starter Code

This directory contains the starter code for the Udatracker project. The initial structure of directories and files is described below.

## Screenshots

A few screenshots taken from the running Flask web app are available under `docs/img/screenshots`:

- `Screenshot 2026-07-30 210405.png`
- `Screenshot 2026-07-30 210501.png`
- `Screenshot 2026-07-30 210535.png`

## Reflection

- **Design decision:** I kept all business rules in `OrderTracker` (duplicate detection, input/status validation) so the Flask routes only parse requests and translate exceptions into HTTP responses. This keeps the API thin and the logic framework-agnostic, making it trivial to swap in a different web framework or storage later.
- **Testing insight:** Writing the `update_order_status` test to assert that storage is *not* read for an invalid status (fail fast) caught an accidental inefficiency during refactoring, and it documents the intended ordering of validation.
- **Next-step improvement:** The most valuable addition would be a `DELETE /api/orders/<order_id>` endpoint and replacing the in-memory storage with a persistent backend so orders survive server restarts.

```
.
├── backend
│   ├── __init__.py
│   ├── app.py
│   ├── in_memory_storage.py
│   ├── order_tracker.py
│   ├── requirements.txt
│   └── tests
│       ├── __init__.py
│       ├── test_api.py
│       └── test_order_tracker.py
├── frontend
│   ├── css
│   │   └── style.css
│   ├── index.html
│   └── js
│       └── script.js
├── pytest.ini
└── README.md
```
