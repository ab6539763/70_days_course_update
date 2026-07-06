#!/usr/bin/env bash
# Day 31 · 一键安装依赖并运行 RAG 调参实验
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
  echo "[run.sh] 已复制 code/.env.example → code/.env（mock 模式）"
fi

cd "$CODE"
exec python3 rag_tuning_lab.py
