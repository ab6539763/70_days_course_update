#!/usr/bin/env bash
# Day 45 · 一键安装依赖并启动 Agent 综合复盘
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
exec python3 integrated_agent_review.py
