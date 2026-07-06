#!/usr/bin/env bash
# Day 32 · 一键运行高级 RAG 演示
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
echo "=== query_rewrite_demo ==="
python3 query_rewrite_demo.py
echo ""
echo "=== multi_query_retriever ==="
python3 multi_query_retriever.py
echo ""
echo "=== hyde_demo ==="
python3 hyde_demo.py
