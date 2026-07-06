#!/usr/bin/env bash
# Day 26 · LCEL 演示一键运行
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

cd "$CODE"
echo "=== lcel_chain_demo ==="
python lcel_chain_demo.py
echo ""
echo "=== translation_chain ==="
python translation_chain.py
