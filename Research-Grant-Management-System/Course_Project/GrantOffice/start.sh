#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
  .venv/bin/python -m pip install -r requirements-lock.txt
fi
.venv/bin/python scripts/setup_users.py
printf 'Open http://127.0.0.1:8000 — login details: runtime/FIRST_LOGIN.txt\n'
exec .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
