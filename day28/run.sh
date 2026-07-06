#!/usr/bin/env bash
# Day 28 一键演示
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
python3 ensure_samples.py
python3 doc_loader_demo.py
python3 text_splitter_demo.py
python3 process_pdf_ebook.py
echo ""
echo "[OK] Day 28 run.sh 完成"
