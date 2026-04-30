# Intelligent Restaurant Management System (IRMS)

**HCMUT — Software Architecture (CO3001) — Semester 252 — Group 2 (CC01)**

## Overview

IRMS is a service-based restaurant management system built around a single FastAPI backend, a Postgres database, and two React frontends (Order taking and Kitchen Display System). The system is partitioned into eight domain modules — Ordering, Menu, Table, KDS, Payment, Inventory, Analytics, and Administration — of which the first four are implemented and the remaining four are documented as future work. Architecture decisions, class diagrams, and the SOLID analysis are kept under `docs/`.

## Group 2 — CC01

| Name | Student ID |
|---|---|
| Bui Quoc Thai | 2353086 |
| Nguyen Vinh Anh Quan | 2353007 |
| Le Thi Phuong Thao | 2252757 |
| Huynh Ngoc Van | 2252898 |
| Nguyen Thuy Tien | 2252806 |

## Quick start

Requires Docker Desktop and Node.js 18+.

```powershell
.\start-demo.ps1                       # Windows: backend + both frontends, auto-seeds on first run
.\start-demo.ps1 -Backend              # only backend (API + Postgres + auto-seed)
.\start-demo.ps1 -Order                # only Order frontend (port 5173)
.\start-demo.ps1 -Kds                  # only KDS frontend (port 5174)
```

```bash
./start-demo.sh                        # macOS / Linux: backend + both frontends
./start-demo.sh --backend              # only backend
./start-demo.sh --order                # only Order frontend
./start-demo.sh --kds                  # only KDS frontend
```

After startup:

- Order UI — http://localhost:5173
- KDS UI — http://localhost:5174
- Swagger — http://localhost:8000/docs

Use `-Reset` (PowerShell) or `--reset` (Bash) to wipe the Postgres volume and re-seed.

## Manual setup (without start-demo)

Use this if you want to start each component yourself, debug a specific layer, or work without the helper script.

### 1. Backend (Docker + Postgres + FastAPI)

```bash
docker compose up -d                # build/start API container + Postgres
docker compose logs -f api          # tail logs (optional)
```

Wait until `http://localhost:8000/health` returns 200, then verify Swagger at `http://localhost:8000/docs`.

To stop: `docker compose down` (or `docker compose down -v` to also wipe the Postgres volume).

### 2. Seed the database

The seed script populates menu categories, menu items, stations, and tables. Run it after the API container is up:

```bash
docker compose exec -T api python -m scripts.seed
```

The seed is idempotent at the *category* level — `start-demo` skips it when categories already exist; running it manually on a non-empty DB may add duplicate rows. Use `docker compose down -v` first if you want a clean re-seed.

### 3. Order frontend (port 5173)

```bash
cd frontend-order
npm install                         # first time only
npm run dev
```

Opens at http://localhost:5173. Vite proxies `/api/*` to the backend on port 8000.

### 4. KDS frontend (port 5174)

```bash
cd frontend_kds
npm install                         # first time only
npm run dev
```

Opens at http://localhost:5174.

### Stopping everything

- Frontends: `Ctrl+C` in each terminal.
- Backend + DB: `docker compose down`.
- Backend + DB + data: `docker compose down -v`.
