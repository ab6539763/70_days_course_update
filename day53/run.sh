#!/bin/bash
set -e
cd "$(dirname "$0")/code"
export SPARKTECH_MOCK=1
python3 verify_day53.py
echo ""
echo "✅ Day 53 验收通过"
