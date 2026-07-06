#!/bin/bash
set -e
cd "$(dirname "$0")/code"
export SPARKTECH_MOCK=1
python3 verify_day52.py
echo ""
echo "✅ Day 52 验收通过"
