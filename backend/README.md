# IRMS Backend

FastAPI + PostgreSQL. Tables are created from ORM models on startup — no migrations.

## Prerequisites

- Python 3.12+
- Docker + Docker Compose

## Local dev (DB in Docker, API on host)

From the repo root:

```bash
docker compose up postgres -d
```

Then in `backend/`:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

- API: http://localhost:8000
- Docs: http://localhost:8000/docs

## Seed demo data

In another terminal with the venv activated:

```bash
cd backend
python -m scripts.seed
```

## Full Docker

```bash
docker compose up
```

## Reset the database

Drops every table and recreates from models on next startup:

```bash
docker compose down -v
docker compose up postgres -d
```

## Inspect the database

```bash
docker compose exec postgres psql -U irms -d irms
```

Inside psql: `\dt` lists tables, `SELECT * FROM menu_item;` etc.
