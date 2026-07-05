#!/usr/bin/env bash
# Day 14 Stage Project 1 · 一键启动命令行助手（mock 模式无需 API Key）
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

if [[ ! -d .venv ]]; then
  if python3 -m venv .venv 2>/dev/null; then
    :
  else
    echo "[提示] 无法创建 venv，将使用系统 Python。可安装 python3-venv 后重试。"
    rm -rf .venv
  fi
fi

if [[ -f .venv/bin/activate ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

pip install -q -r requirements.txt

export SPARKTECH_MOCK="${SPARKTECH_MOCK:-1}"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"

python3 -m project1.main "$@"
