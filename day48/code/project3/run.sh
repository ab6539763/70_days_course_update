#!/usr/bin/env bash
# Project 3 · 多 Agent 智能办公助手 — 一键启动
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$ROOT/.venv"
BACKEND_PORT="${BACKEND_PORT:-8010}"
FRONTEND_PORT="${FRONTEND_PORT:-8088}"

if [[ ! -d "$VENV" ]]; then
  if python3 -m venv "$VENV" 2>/dev/null; then
    :
  else
    echo "[run.sh] venv 不可用，使用系统 Python"
    VENV=""
  fi
fi

if [[ -n "$VENV" ]] && [[ -f "$VENV/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source "$VENV/bin/activate"
  pip install -q -r "$ROOT/requirements.txt"
else
  pip install -q --user -r "$ROOT/requirements.txt" 2>/dev/null || pip install -q -r "$ROOT/requirements.txt"
fi

if [[ ! -f "$ROOT/.env" ]] && [[ -f "$ROOT/.env.example" ]]; then
  cp "$ROOT/.env.example" "$ROOT/.env"
  echo "[run.sh] 已复制 .env.example → .env（mock 模式）"
fi

mkdir -p "$ROOT/data/checkpoints" "$ROOT/data/sample_docs"

cleanup() {
  echo ""
  echo "[run.sh] 正在停止服务…"
  [[ -n "${BACKEND_PID:-}" ]] && kill "$BACKEND_PID" 2>/dev/null || true
  [[ -n "${FRONTEND_PID:-}" ]] && kill "$FRONTEND_PID" 2>/dev/null || true
  wait 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "=========================================="
echo " Project 3 · 多 Agent 智能办公助手"
echo " 后端 API : http://127.0.0.1:${BACKEND_PORT}"
echo " 前端页面 : http://127.0.0.1:${FRONTEND_PORT}"
echo " API 文档 : http://127.0.0.1:${BACKEND_PORT}/docs"
echo "=========================================="
echo ""

cd "$ROOT"
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
export SPARKTECH_MOCK="${SPARKTECH_MOCK:-1}"

uvicorn backend.main:app --host 0.0.0.0 --port "$BACKEND_PORT" &
BACKEND_PID=$!

sleep 1

python3 -m http.server "$FRONTEND_PORT" --directory "$ROOT/frontend" &
FRONTEND_PID=$!

echo "[run.sh] 后端 PID=$BACKEND_PID  前端 PID=$FRONTEND_PID"
echo "[run.sh] 按 Ctrl+C 停止"
echo ""

wait
