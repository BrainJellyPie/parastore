#!/usr/bin/env bash
# Run backend (uvicorn) and frontend (vite) concurrently for local dev.
# Usage: ./scripts/dev.sh
#
# Prereqs:
#   - uv installed (https://github.com/astral-sh/uv)
#   - pnpm installed (>=10.x)
#   - backend/.env populated with LLM API keys (see backend/.env.example)
#
# Ctrl-C terminates both processes.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cleanup() {
  jobs -p | xargs -r kill 2>/dev/null || true
}
trap cleanup EXIT INT TERM

cd "$ROOT/backend"
uv sync --quiet
#uv run uvicorn store_emulator.server.main:app --reload
uv run uvicorn store_emulator.server.main:app --reload --host 0.0.0.0 --port 8000 &

cd "$ROOT/frontend"
pnpm install --silent
pnpm dev &

wait
