#!/usr/bin/env bash
# 一键提示：分别启动后端与前端开发服务
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
echo "后端: cd $ROOT/backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000"
echo "前端: cd $ROOT/frontend && npm run dev"
