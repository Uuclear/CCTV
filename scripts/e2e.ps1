# End-to-end: install Chromium once, then run Playwright (from repo root)
$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
if ((Split-Path -Leaf $root) -eq "scripts") {
  $root = Split-Path $root -Parent
}
Set-Location "$root/frontend"
if (-not (Test-Path "node_modules/@playwright/test")) {
  Write-Host "Run init.ps1 first."
  exit 1
}
Write-Host "Installing Playwright Chromium (one-time, ~200MB)..."
npx playwright install chromium
Write-Host "Running E2E..."
npx playwright test
