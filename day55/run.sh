#!/bin/bash
set -e
cd "$(dirname "$0")/code"
export SPARKTECH_MOCK=1
python3 verify_day55.py
echo ""
echo "✅ Day 55 验收通过"
