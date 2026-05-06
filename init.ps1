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

Write-Host "== Installing frontend deps =="
Push-Location "$root/frontend"
if (-not (Test-Path "package.json")) { throw "frontend/package.json missing" }
npm install
Pop-Location

Write-Host ""
Write-Host "Done."
Write-Host "Backend:  cd backend; .\.venv\Scripts\Activate.ps1; uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
Write-Host "Frontend: cd frontend; npm run dev"
Write-Host "See AGENTS.md"
