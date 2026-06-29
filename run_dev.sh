#!/usr/bin/env bash
set -euo pipefail
if [ ! -d ".venv" ]; then
  python -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python -m uvicorn app:app --reload --port 8000
