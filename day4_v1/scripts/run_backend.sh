#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
exec uvicorn backend.app.main:app --reload --host "${BACKEND_HOST:-0.0.0.0}" --port "${BACKEND_PORT:-8000}"
