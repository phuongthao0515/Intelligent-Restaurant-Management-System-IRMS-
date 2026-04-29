# Start IRMS demo: bring up Docker, wait for API, seed if empty, open Swagger.
#
# Usage:
#   .\start-demo.ps1            # normal start (preserves existing data)
#   .\start-demo.ps1 -Reset     # wipe Postgres volume first (fresh schema)
#   .\start-demo.ps1 -NoBrowser # skip opening browser
#
# Requires: Docker Desktop running.

param(
    [switch]$Reset,
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"
$API = "http://localhost:8000"

# 0. Pre-check: Docker Engine running?
# Use cmd.exe wrapper to discard stderr at OS level (avoids PowerShell
# wrapping Docker CLI plugin warnings as ErrorRecord under ErrorAction=Stop).
Write-Host "[0/5] Checking Docker..." -ForegroundColor Cyan
cmd /c "docker info >nul 2>&1"
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Docker Desktop is not running." -ForegroundColor Red
    Write-Host "Please:"
    Write-Host "  1. Open Docker Desktop from Start menu"
    Write-Host "  2. Wait for the whale icon in taskbar to turn green"
    Write-Host "  3. Run this script again"
    Write-Host ""
    Write-Host "If Docker Desktop is not installed:" -ForegroundColor Yellow
    Write-Host "  Download from https://www.docker.com/products/docker-desktop"
    exit 1
}
Write-Host "  Docker is running." -ForegroundColor Green

# 1. Optional reset (wipes pgdata volume so init_db rebuilds schema)
if ($Reset) {
    Write-Host "[1/5] Wiping Postgres volume..." -ForegroundColor Yellow
    docker compose down -v
    if ($LASTEXITCODE -ne 0) { throw "docker compose down -v failed" }
}

# 2. Start containers (detached)
Write-Host "[2/5] Starting Docker containers..." -ForegroundColor Cyan
docker compose up -d
if ($LASTEXITCODE -ne 0) { throw "docker compose up -d failed" }

# 3. Wait for API to be reachable (max 60s)
Write-Host "[3/5] Waiting for API to come up..." -ForegroundColor Cyan
$ready = $false
for ($i = 1; $i -le 60; $i++) {
    try {
        $r = Invoke-WebRequest -Uri "$API/health" -UseBasicParsing -TimeoutSec 2
        if ($r.StatusCode -eq 200) {
            $ready = $true
            break
        }
    } catch {
        # not ready yet
    }
    Start-Sleep -Seconds 1
    if ($i % 5 -eq 0) { Write-Host "  ...still waiting ($i s)" }
}

if (-not $ready) {
    Write-Host "API did not become ready in 60s. Check docker compose logs api" -ForegroundColor Red
    throw "API health check timeout"
}
Write-Host "  API is up." -ForegroundColor Green

# 4. Seed if empty
Write-Host "[4/5] Checking seed state..." -ForegroundColor Cyan
$categories = Invoke-RestMethod -Uri "$API/api/v1/menu/categories"
if ($categories.Count -eq 0) {
    Write-Host "  Database empty - running seed..." -ForegroundColor Yellow
    docker compose exec -T api python -m scripts.seed
    if ($LASTEXITCODE -ne 0) { throw "seed failed" }
    Write-Host "  Seed complete." -ForegroundColor Green
} else {
    Write-Host "  Already seeded ($($categories.Count) categories). Skipping." -ForegroundColor Green
}

# 5. Summary + open browser
Write-Host ""
Write-Host "========== READY ==========" -ForegroundColor Green
$counts = @{
    Categories = (Invoke-RestMethod "$API/api/v1/menu/categories").Count
    MenuItems  = (Invoke-RestMethod "$API/api/v1/menu/items").Count
    Stations   = (Invoke-RestMethod "$API/api/v1/kds/stations").Count
    Tables     = (Invoke-RestMethod "$API/api/v1/tables").Count
}
$counts.GetEnumerator() | ForEach-Object {
    Write-Host ("  {0,-12} {1}" -f $_.Key, $_.Value)
}

Write-Host ""
Write-Host "Endpoints:"
Write-Host "  Swagger UI : $API/docs"
Write-Host "  ReDoc      : $API/redoc"
Write-Host "  OpenAPI    : $API/openapi.json"
Write-Host "  Health     : $API/health"
Write-Host ""

if (-not $NoBrowser) {
    Write-Host "Opening Swagger UI in browser..." -ForegroundColor Cyan
    Start-Process "$API/docs"
}

Write-Host "Done. To stop: docker compose down" -ForegroundColor Gray
