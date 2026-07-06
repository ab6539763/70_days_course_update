#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CODE="$ROOT/code"
VENV="$ROOT/.venv"
[[ -d "$VENV" ]] || python3 -m venv "$VENV"
# shellcheck disable=SC1091
source "$VENV/bin/activate"
pip install -q -r "$CODE/requirements.txt"
[[ -f "$CODE/.env" ]] || [[ ! -f "$CODE/.env.example" ]] || cp "$CODE/.env.example" "$CODE/.env"
cd "$CODE"
export SPARKTECH_MOCK=1
exec python3 lc_agent.py
