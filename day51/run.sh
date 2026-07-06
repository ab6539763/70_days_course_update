#!/bin/bash
set -e
cd "$(dirname "$0")/code"
export SPARKTECH_MOCK=1
python3 verify_day51.py
echo ""
echo "✅ Day 51 验收通过"
