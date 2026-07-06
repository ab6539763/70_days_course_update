#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT/code"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q -r requirements.txt

export SPARKTECH_MOCK=1
python3 build_vectorstore.py
python3 similarity_search_demo.py
python3 verify_day29.py
echo ""
echo "[OK] Day 29 run.sh 完成"
