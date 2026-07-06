#!/usr/bin/env bash
# Day 23 · 一键安装依赖并启动 FastAPI
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
exec uvicorn main:app --reload --host 127.0.0.1 --port 8000
