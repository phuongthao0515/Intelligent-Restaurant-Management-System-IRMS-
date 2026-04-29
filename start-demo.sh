#!/usr/bin/env bash
# Start IRMS demo: backend, order frontend, KDS frontend.
#
# Usage:
#   ./start-demo.sh             # everything (default)
#   ./start-demo.sh --backend   # only backend
#   ./start-demo.sh --order     # only frontend-order (5173)
#   ./start-demo.sh --kds       # only frontend_kds (5174)
#   ./start-demo.sh --reset     # wipe Postgres before starting
#   ./start-demo.sh --no-browser # skip opening browser tabs
#
# Requires: Docker, Node.js 18+ with npm. Optional: jq.

set -euo pipefail

API="http://localhost:8000"
ORDER_URL="http://localhost:5173"
KDS_URL="http://localhost:5174"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

BACKEND=false
ORDER=false
KDS=false
RESET=false
NO_BROWSER=false

for arg in "$@"; do
  case "$arg" in
    --backend) BACKEND=true ;;
    --order) ORDER=true ;;
    --kds) KDS=true ;;
    --reset) RESET=true ;;
    --no-browser) NO_BROWSER=true ;;
    -h|--help)
      sed -n '2,11p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *) echo "Unknown flag: $arg" >&2; exit 1 ;;
  esac
done

if ! $BACKEND && ! $ORDER && ! $KDS; then
  BACKEND=true; ORDER=true; KDS=true
fi

open_url() {
  local url="$1"
  if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$url" >/dev/null 2>&1 &
  elif command -v open >/dev/null 2>&1; then
    open "$url"
  fi
}

PIDS=()

start_frontend() {
  local name="$1" port="$2" path="$3"
  if [ ! -d "$path" ]; then
    echo "  $name directory not found at $path - skipping."
    return
  fi
  if [ ! -d "$path/node_modules" ]; then
    echo "  Installing $name dependencies (first run, ~1-2 min)..."
    (cd "$path" && npm install)
  fi
  echo "  Launching $name on :$port..."
  (cd "$path" && npm run dev) &
  PIDS+=($!)
}

cleanup() {
  if [ ${#PIDS[@]} -gt 0 ]; then
    echo ""
    echo "Stopping frontends (pids: ${PIDS[*]})..."
    kill "${PIDS[@]}" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

if $BACKEND; then
  echo "[Backend] Checking Docker..."
  if ! docker info >/dev/null 2>&1; then
    echo "Docker is not running. Start Docker, then re-run."
    exit 1
  fi
  echo "  Docker is running."

  if $RESET; then
    echo "[Backend] Wiping Postgres volume..."
    docker compose down -v
  fi

  echo "[Backend] Starting Docker containers..."
  docker compose up -d

  echo "[Backend] Waiting for API..."
  ready=false
  for i in $(seq 1 60); do
    if curl -fsS "$API/health" >/dev/null 2>&1; then
      ready=true; break
    fi
    sleep 1
    if (( i % 5 == 0 )); then echo "  ...still waiting (${i}s)"; fi
  done
  if ! $ready; then
    echo "API did not become ready in 60s. Check 'docker compose logs api'"
    exit 1
  fi
  echo "  API is up."

  echo "[Backend] Checking seed state..."
  cat_count=$(curl -fsS "$API/api/v1/menu/categories" | grep -o '"id"' | wc -l || echo 0)
  if [ "$cat_count" -eq 0 ]; then
    echo "  Database empty - running seed..."
    docker compose exec -T api python -m scripts.seed
    echo "  Seed complete."
  else
    echo "  Already seeded ($cat_count categories). Skipping."
  fi
fi

if $ORDER; then
  echo "[Order] Starting frontend-order..."
  start_frontend "frontend-order" 5173 "$REPO_ROOT/frontend-order"
fi

if $KDS; then
  echo "[Kds] Starting frontend_kds..."
  start_frontend "frontend_kds" 5174 "$REPO_ROOT/frontend_kds"
fi

if $ORDER || $KDS; then
  echo "  Waiting for frontends to compile..."
  sleep 6
fi

echo ""
echo "========== READY =========="
echo "Endpoints:"
$ORDER   && echo "  Order UI    : $ORDER_URL"
$KDS     && echo "  KDS UI      : $KDS_URL"
$BACKEND && echo "  Swagger     : $API/docs"
$BACKEND && echo "  Health      : $API/health"
echo ""

if ! $NO_BROWSER; then
  $ORDER && open_url "$ORDER_URL" && sleep 0.4
  $KDS   && open_url "$KDS_URL"   && sleep 0.4
fi

echo "To stop:"
echo "  - Ctrl+C here (kills frontends)"
echo "  - docker compose down"

if [ ${#PIDS[@]} -gt 0 ]; then
  wait
fi
