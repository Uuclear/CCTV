# Install ffmpeg (system) and ensure rapidocr in backend venv
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$py = Join-Path $root "backend\.venv\Scripts\python.exe"
$pip = Join-Path $root "backend\.venv\Scripts\pip.exe"

Write-Host "== rapidocr (venv) =="
if (-not (Test-Path $py)) {
    Write-Host "Run init.ps1 first to create backend\.venv" -ForegroundColor Yellow
    exit 1
}
& $pip install "rapidocr-onnxruntime>=1.3,<2"
& $py -c "from rapidocr_onnxruntime import RapidOCR; RapidOCR(); print('rapidocr OK')"

Write-Host "== ffmpeg (system PATH) =="
$ff = Get-Command ffmpeg -ErrorAction SilentlyContinue
if ($ff) {
    & ffmpeg -version | Select-Object -First 1
    Write-Host "ffmpeg already on PATH: $($ff.Source)" -ForegroundColor Green
    exit 0
}

if (Get-Command winget -ErrorAction SilentlyContinue) {
    Write-Host "Installing ffmpeg via winget..."
    winget install --id Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements
} elseif (Get-Command choco -ErrorAction SilentlyContinue) {
    choco install ffmpeg -y
} else {
    Write-Host "winget/choco not found. Install ffmpeg manually: https://ffmpeg.org/download.html" -ForegroundColor Yellow
    exit 1
}

$ff2 = Get-Command ffmpeg -ErrorAction SilentlyContinue
if ($ff2) {
    Write-Host "ffmpeg installed: $($ff2.Source)" -ForegroundColor Green
} else {
    Write-Host "ffmpeg installed; restart terminal to refresh PATH." -ForegroundColor Yellow
}
