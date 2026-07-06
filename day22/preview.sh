#!/usr/bin/env bash
# Day 22 · 本地静态文件预览（避免 file:// 下 fetch 受限）
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATIC="$ROOT/static"
PORT="${PORT:-8080}"

echo "星火智服 Day 22 静态原型"
echo "目录: $STATIC"
echo "访问: http://127.0.0.1:${PORT}"
echo "按 Ctrl+C 停止"
echo ""

cd "$STATIC"
exec python3 -m http.server "$PORT"
