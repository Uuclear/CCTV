# One-command dev bootstrap (Windows)
$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
Set-Location $root

Write-Host "== CCTV-report: creating backend venv and installing deps =="
if (-not (Test-Path "$root/backend/.venv")) {
    python -m venv "$root/backend/.venv"
}
& "$root/backend/.venv/Scripts/python.exe" -m pip install --upgrade pip
& "$root/backend/.venv/Scripts/pip.exe" install -r "$root/backend/requirements.txt"

Write-Host "== Installing frontend deps (Playwright browsers skipped; run scripts/e2e.ps1 for E2E) =="
Push-Location "$root/frontend"
if (-not (Test-Path "package.json")) { throw "frontend/package.json missing" }
$env:PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD = "1"
npm install
Remove-Item Env:PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD -ErrorAction SilentlyContinue
Pop-Location

Write-Host ""
Write-Host "Done."
Write-Host "Backend:  cd backend; .\.venv\Scripts\Activate.ps1; uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
Write-Host "Frontend: cd frontend; npm run dev"
Write-Host "See AGENTS.md"
