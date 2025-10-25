#!/usr/bin/env bash
# run.sh - script d'aide pour Linux/macOS
set -euo pipefail

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
[ -f requirements.txt ] && pip install -r requirements.txt
python willkommen_v2.py
