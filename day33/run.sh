#!/usr/bin/env bash
# Day 33 · 一键运行 Hybrid + Rerank + 增强管道
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
echo "=== hybrid_retriever ==="
python3 hybrid_retriever.py
echo ""
echo "=== rerank_demo ==="
python3 rerank_demo.py
echo ""
echo "=== enhanced_rag_pipeline ==="
python3 enhanced_rag_pipeline.py
