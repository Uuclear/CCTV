# 本地同时启动后端 + 前端（Windows，非 Tauri）
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root

$py = Join-Path $root "backend\.venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
  Write-Host "请先运行根目录 init.ps1" -ForegroundColor Yellow
  exit 1
}

$job1 = Start-Process -FilePath $py -ArgumentList @(
  "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"
) -WorkingDirectory (Join-Path $root "backend") -PassThru

Start-Sleep -Seconds 2
$job2 = Start-Process -FilePath "npm" -ArgumentList @("run", "dev") -WorkingDirectory (Join-Path $root "frontend") -PassThru

Write-Host "后端 PID $($job1.Id)、前端 PID $($job2.Id)。关闭对应进程即可停止。" -ForegroundColor Green
Write-Host "浏览器打开 http://127.0.0.1:5173" 
Write-Host "按 Enter 退出（不会自动杀进程）..."
$null = Read-Host
