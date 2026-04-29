# Start IRMS demo: backend, order frontend, KDS frontend.
#
# Usage:
#   .\start-demo.ps1            # everything (default)
#   .\start-demo.ps1 -Backend   # only backend
#   .\start-demo.ps1 -Order     # only frontend-order (5173)
#   .\start-demo.ps1 -Kds       # only frontend_kds (5174)
#   .\start-demo.ps1 -Reset     # wipe Postgres before starting
#   .\start-demo.ps1 -NoBrowser # skip opening browser tabs
#
# Requires: Docker Desktop running, Node.js 18+ with npm.

param(
    [switch]$Backend,
    [switch]$Kds,
    [switch]$Order,
    [switch]$Reset,
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"
$API = "http://localhost:8000"
$ORDER_URL = "http://localhost:5173"
$KDS_URL = "http://localhost:5174"
$RepoRoot = $PSScriptRoot

$runAll = -not ($Backend -or $Kds -or $Order)
$doBackend = $runAll -or $Backend
$doOrder   = $runAll -or $Order
$doKds     = $runAll -or $Kds

function Start-FrontendApp($name, $port, $path) {
    if (-not (Test-Path $path)) {
        Write-Host "  $name directory not found at $path - skipping." -ForegroundColor Yellow
        return
    }
    $nodeModules = Join-Path $path "node_modules"
    if (-not (Test-Path $nodeModules)) {
        Write-Host "  Installing $name dependencies (first run, ~1-2 min)..." -ForegroundColor Yellow
        Push-Location $path
        npm install
        $npmExit = $LASTEXITCODE
        Pop-Location
        if ($npmExit -ne 0) { throw "npm install failed for $name" }
    }
    Write-Host "  Launching $name on :$port..." -ForegroundColor Green
    $cmd = "Set-Location '$path'; Write-Host 'Starting $name on :$port' -ForegroundColor Cyan; npm run dev"
    Start-Process powershell.exe -ArgumentList "-NoExit", "-Command", $cmd
}

if ($doBackend) {
    Write-Host "[Backend] Checking Docker..." -ForegroundColor Cyan
    cmd /c "docker info >nul 2>&1"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Docker Desktop is not running. Open it, wait for the whale icon to turn green, then re-run." -ForegroundColor Red
        exit 1
    }
    Write-Host "  Docker is running." -ForegroundColor Green

    if ($Reset) {
        Write-Host "[Backend] Wiping Postgres volume..." -ForegroundColor Yellow
        docker compose down -v
        if ($LASTEXITCODE -ne 0) { throw "docker compose down -v failed" }
    }

    Write-Host "[Backend] Starting Docker containers..." -ForegroundColor Cyan
    docker compose up -d
    if ($LASTEXITCODE -ne 0) { throw "docker compose up -d failed" }

    Write-Host "[Backend] Waiting for API..." -ForegroundColor Cyan
    $ready = $false
    for ($i = 1; $i -le 60; $i++) {
        try {
            $r = Invoke-WebRequest -Uri "$API/health" -UseBasicParsing -TimeoutSec 2
            if ($r.StatusCode -eq 200) { $ready = $true; break }
        } catch {}
        Start-Sleep -Seconds 1
        if ($i % 5 -eq 0) { Write-Host "  ...still waiting ($i s)" }
    }
    if (-not $ready) {
        Write-Host "API did not become ready in 60s. Check 'docker compose logs api'" -ForegroundColor Red
        throw "API health check timeout"
    }
    Write-Host "  API is up." -ForegroundColor Green

    Write-Host "[Backend] Checking seed state..." -ForegroundColor Cyan
    $categories = Invoke-RestMethod -Uri "$API/api/v1/menu/categories"
    if ($categories.Count -eq 0) {
        Write-Host "  Database empty - running seed..." -ForegroundColor Yellow
        docker compose exec -T api python -m scripts.seed
        if ($LASTEXITCODE -ne 0) { throw "seed failed" }
        Write-Host "  Seed complete." -ForegroundColor Green
    } else {
        Write-Host "  Already seeded ($($categories.Count) categories). Skipping." -ForegroundColor Green
    }
}

if ($doOrder) {
    Write-Host "[Order] Starting frontend-order..." -ForegroundColor Cyan
    Start-FrontendApp "frontend-order" 5173 (Join-Path $RepoRoot "frontend-order")
}

if ($doKds) {
    Write-Host "[Kds] Starting frontend_kds..." -ForegroundColor Cyan
    Start-FrontendApp "frontend_kds" 5174 (Join-Path $RepoRoot "frontend_kds")
}

if ($doOrder -or $doKds) {
    Write-Host "  Waiting for frontends to compile..." -ForegroundColor Cyan
    Start-Sleep -Seconds 6
}

Write-Host ""
Write-Host "========== READY ==========" -ForegroundColor Green
if ($doBackend) {
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
}

Write-Host "Endpoints:"
if ($doOrder)   { Write-Host "  Order UI    : $ORDER_URL" }
if ($doKds)     { Write-Host "  KDS UI      : $KDS_URL" }
if ($doBackend) { Write-Host "  Swagger     : $API/docs" }
if ($doBackend) { Write-Host "  Health      : $API/health" }
Write-Host ""

if (-not $NoBrowser) {
    if ($doOrder) { Start-Process $ORDER_URL; Start-Sleep -Milliseconds 400 }
    if ($doKds)   { Start-Process $KDS_URL;   Start-Sleep -Milliseconds 400 }
}

Write-Host "To stop:" -ForegroundColor Gray
Write-Host "  - Close any frontend PowerShell windows (Ctrl+C in each)"
Write-Host "  - docker compose down"
