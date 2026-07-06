#!/usr/bin/env bash
# Day 44 · MCP Server + Client + Agent 一键演示
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CODE="$ROOT/code"
VENV="$ROOT/.venv"

if [[ ! -d "$VENV" ]]; then
  python3 -m venv "$VENV"
fi

# shellcheck disable=SC1091
source "$VENV/bin/activate"
pip install -q -r "$CODE/requirements.txt" || pip install -q langchain-core langchain-community python-dotenv

if [[ ! -f "$CODE/.env" ]] && [[ -f "$CODE/.env.example" ]]; then
  cp "$CODE/.env.example" "$CODE/.env"
fi

cd "$CODE"
echo "=== simple_mcp_server ==="
python3 simple_mcp_server.py
echo ""
echo "=== mcp_client_demo ==="
python3 mcp_client_demo.py
echo ""
echo "=== agent_with_mcp ==="
python3 agent_with_mcp.py
echo ""
echo "=== verify_day44 ==="
python3 verify_day44.py
