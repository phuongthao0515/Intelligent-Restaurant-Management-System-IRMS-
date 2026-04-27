#!/usr/bin/env bash

# Usage:
#   ./start-demo.sh            # normal start
#   ./start-demo.sh --reset    # wipe Postgres volume
#   ./start-demo.sh --no-browser

set -e

API="http://localhost:8000"
RESET=false
NO_BROWSER=false

# Parse args
for arg in "$@"; do
  case $arg in
    --reset) RESET=true ;;
    --no-browser) NO_BROWSER=true ;;
  esac
done

echo "[0/5] Checking Docker..."

if ! docker info > /dev/null 2>&1; then
  echo ""
  echo "Docker is not running."
  echo "Please start Docker and try again."
  exit 1
fi
echo "  Docker is running."

# 1. Optional reset
if [ "$RESET" = true ]; then
  echo "[1/5] Wiping Postgres volume..."
  docker compose down -v
fi

# 2. Start containers
echo "[2/5] Starting Docker containers..."
docker compose up -d

# 3. Wait for API
echo "[3/5] Waiting for API to come up..."
ready=false

for i in {1..60}; do
  if curl -s "$API/health" > /dev/null; then
    ready=true
    break
  fi

  sleep 1
  if (( i % 5 == 0 )); then
    echo "  ...still waiting ($i s)"
  fi
done

if [ "$ready" = false ]; then
  echo "API did not become ready in 60s. Check logs:"
  echo "  docker compose logs api"
  exit 1
fi
echo "  API is up."

# 4. Seed if empty
echo "[4/5] Checking seed state..."
categories=$(curl -s "$API/api/v1/menu/categories")

if [ "$categories" = "[]" ]; then
  echo "  Database empty - running seed..."
  docker compose exec -T api python -m scripts.seed
  echo "  Seed complete."
else
  count=$(echo "$categories" | jq length)
  echo "  Already seeded ($count categories). Skipping."
fi

# 5. Summary
echo ""
echo "========== READY =========="

get_count () {
  curl -s "$1" | jq length
}

echo "  Categories  $(get_count "$API/api/v1/menu/categories")"
echo "  MenuItems   $(get_count "$API/api/v1/menu/items")"
echo "  Stations    $(get_count "$API/api/v1/kds/stations")"
echo "  Tables      $(get_count "$API/api/v1/tables")"

echo ""
echo "Endpoints:"
echo "  Swagger UI : $API/docs"
echo "  ReDoc      : $API/redoc"
echo "  OpenAPI    : $API/openapi.json"
echo "  Health     : $API/health"
echo ""

# Open browser
if [ "$NO_BROWSER" = false ]; then
  echo "Opening Swagger UI in browser..."
  xdg-open "$API/docs" > /dev/null 2>&1 || true
fi

echo "Done. To stop: docker compose down"