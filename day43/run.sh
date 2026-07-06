#!/usr/bin/env bash
# Day 43 · Multi-Agent Supervisor 一键演示
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CODE="$ROOT/code"
VENV="$ROOT/.venv"

if [[ ! -d "$VENV" ]]; then
  python3 -m venv "$VENV"
fi

# shellcheck disable=SC1091
source "$VENV/bin/activate"
pip install -q -r "$CODE/requirements.txt"

if [[ ! -f "$CODE/.env" ]] && [[ -f "$CODE/.env.example" ]]; then
  cp "$CODE/.env.example" "$CODE/.env"
fi

cd "$CODE"
echo "=== supervisor_multi_agent ==="
python3 supervisor_multi_agent.py
echo ""
echo "=== verify_day43 ==="
python3 verify_day43.py
