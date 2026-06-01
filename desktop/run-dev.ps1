# Local dev: backend :8000 + frontend :5173 (Windows)
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root

$py = Join-Path $root "backend\.venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
  Write-Host "Run init.ps1 first to create backend\.venv" -ForegroundColor Yellow
  exit 1
}

function Stop-OrphanUvicornWorkers {
  Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -match "multiprocessing\.spawn|uvicorn" -and $_.CommandLine -match "CCTV-report" } |
    ForEach-Object {
      Write-Host "Kill orphan Python PID $($_.ProcessId)"
      Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    }
}

function Stop-PortListeners([int]$port) {
  for ($try = 0; $try -lt 8; $try++) {
    $pids = @()
    netstat -ano | Select-String ":$port\s+.*LISTENING" | ForEach-Object {
      if ($_ -match '\s+(\d+)\s*$') { $pids += [int]$Matches[1] }
    }
    $pids = $pids | Sort-Object -Unique
    if (-not $pids.Count) { return }
    foreach ($procId in $pids) {
      if ($procId -gt 0) {
        Write-Host "Kill PID $procId on port $port"
        Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
      }
    }
    Start-Sleep -Milliseconds 600
  }
}

Stop-OrphanUvicornWorkers
Stop-PortListeners 8001
Stop-PortListeners 8000
Stop-PortListeners 5173
Start-Sleep -Seconds 1

Write-Host "Starting backend http://127.0.0.1:8000 ..." -ForegroundColor Green
$backend = Start-Process -FilePath $py -ArgumentList @(
  "-m", "uvicorn", "app.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"
) -WorkingDirectory (Join-Path $root "backend") -PassThru

$ready = $false
for ($i = 0; $i -lt 45; $i++) {
  try {
    $null = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -TimeoutSec 2
    $ready = $true
    break
  }
  catch {
    Start-Sleep -Seconds 1
  }
}
if (-not $ready) {
  Write-Host "WARN: /health not ready within 45s. Check backend window." -ForegroundColor Yellow
}

try {
  $health = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/imports/ocr-status" -TimeoutSec 60
  Write-Host "OCR: $($health | ConvertTo-Json -Compress)" -ForegroundColor Cyan
  $defs = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/standards/defects" -TimeoutSec 10
  $defCount = @($defs).Count
  Write-Host "Defect catalog: $defCount items (need at least 16)" -ForegroundColor Cyan
  if ($defCount -lt 10) {
    Write-Host "ERROR: old backend or missing standards router. Restart uvicorn." -ForegroundColor Red
    exit 1
  }
}
catch {
  Write-Host "WARN: backend self-check failed: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "Starting frontend http://127.0.0.1:5173 ..." -ForegroundColor Green
$frontend = Start-Process -FilePath "npm" -ArgumentList @("run", "dev") -WorkingDirectory (Join-Path $root "frontend") -PassThru

Write-Host ""
Write-Host "Backend PID $($backend.Id), frontend PID $($frontend.Id)." -ForegroundColor Green
Write-Host "Open http://127.0.0.1:5173 in your browser."
Write-Host "Press Enter to close this launcher (child processes keep running)..."
$null = Read-Host
