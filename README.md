# IRMS Backend Skeleton

Project now includes a runnable FastAPI backend skeleton for the two backend modules:

- `Ordering`: menu, tables, orders
- `KDS`: stations, tickets, item status, event log

## Current project structure

```text
app/
  main.py                     # FastAPI entrypoint, mounts REST and WebSocket routers
  shared/                     # Shared building blocks used by all modules
    models.py                 # Pydantic schemas, enums, request/response models
    store.py                  # Temporary in-memory store and sample seed data
    events.py                 # Simple EventBus abstraction
    websocket.py              # ConnectionManager and WebSocketBroadcaster
  modules/
    ordering/                 # Ordering module
      router.py               # REST endpoints for menu, tables, orders
      service.py              # Ordering business logic skeleton
    kds/                      # Kitchen Display System module
      router.py               # REST endpoints for stations, tickets, item status, events
      service.py              # KDS business logic skeleton
      websocket.py            # WebSocket endpoints: /ws/kds, /ws/orders, /ws/menu
docs/
  api.yaml                    # REST API contract
  ws-schema.md                # WebSocket message contract
pyproject.toml                # Python dependencies and project metadata
README.md                     # Setup notes and project overview
```

## What is implemented now

- FastAPI application bootstrap
- REST route skeleton for `Ordering` and `KDS`
- WebSocket route skeleton for station, order, and menu channels
- Shared schemas and enums matching the current API / WS docs
- In-memory data store for early development without a real database

## Recommended next step

- Replace `app/shared/store.py` with a real persistence layer once the team finalizes entities and flow ownership
- Keep the current module split: `Ordering` owns `Order`, `Menu`, `Table`; `KDS` owns `Station`, `Ticket` view, and `OrderItem` workflow
- Add repository layer and database models before implementing full business rules

Run locally:

```bash
uvicorn app.main:app --reload
```

Open docs at `http://localhost:8000/docs`.

## Database note

Right now the project uses an in-memory store only for scaffolding.

For this IRMS assignment, a relational database is usually a better fit than MongoDB because:

- orders, order items, tables, stations, billing, reservations, and audit logs are strongly related
- you will likely need joins, consistent transactions, and strict state transitions
- your architecture notes already lean toward a shared database with logical partitioning

So if the question is "should we move to MongoDB Compass / NoSQL now?", my recommendation is:

- `No` for now, unless your instructor explicitly wants a NoSQL solution
- Prefer `PostgreSQL` or `MySQL` when you start real persistence
- Use `MongoDB Compass` only if the team has already committed to MongoDB for a clear reason

Short version: this kind of restaurant system is more naturally modeled with SQL than NoSQL.
