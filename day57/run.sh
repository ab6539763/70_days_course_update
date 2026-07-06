#!/bin/bash
set -e
cd "$(dirname "$0")/code"
export SPARKTECH_MOCK=1
python3 verify_day57.py
echo ""
echo "可选: cd deploy_stack && docker compose up --build"
