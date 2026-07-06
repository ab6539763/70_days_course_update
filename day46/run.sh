#!/usr/bin/env bash
# Day 46 · 一键运行可观测性与护栏演示
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

cd "$CODE"
python3 agent_guardrails.py
echo "---"
python3 observability_demo.py
echo "---"
python3 retry_agent_wrapper.py
