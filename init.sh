#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "== CCTV-report: backend venv + pip =="
python3 -m venv backend/.venv
# shellcheck disable=SC1091
source backend/.venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt

echo "== frontend npm install (Playwright browser download skipped) =="
cd frontend
export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
npm install
unset PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD || true
cd "$ROOT"

echo "Done. Backend: cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
echo "Frontend: cd frontend && npm run dev"
