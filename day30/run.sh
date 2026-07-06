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
python3 rag_cli.py --mock ingest
python3 rag_cli.py --mock ask "如何申请退款？"
python3 rag_cli.py --mock ask "今天天气怎么样？"
python3 verify_day30.py
echo ""
echo "[OK] Day 30 run.sh 完成"
