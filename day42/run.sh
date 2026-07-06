#!/usr/bin/env bash
# Day 42 · LangGraph 进阶一键演示
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
echo "=== checkpointer_demo ==="
python3 checkpointer_demo.py
echo ""
echo "=== human_in_loop ==="
python3 human_in_loop.py
echo ""
echo "=== writing_agent_graph ==="
python3 writing_agent_graph.py
echo ""
echo "=== verify_day42 ==="
python3 verify_day42.py
