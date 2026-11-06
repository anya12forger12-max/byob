#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
python3 -m venv .venv
.venv/bin/pip install --upgrade pip >/dev/null
.venv/bin/pip install -r byob/requirements.txt
.venv/bin/pip install -r web-gui/requirements.txt
echo "Installed. Console app: .venv/bin/python byob/server.py"
echo "Web GUI: .venv/bin/python web-gui/run.py"
