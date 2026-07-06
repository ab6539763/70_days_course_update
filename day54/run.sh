#!/bin/bash
set -e
cd "$(dirname "$0")/code"
export SPARKTECH_MOCK=1
python3 verify_day54.py
echo ""
echo "✅ Day 54 验收通过"
