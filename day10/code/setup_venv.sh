#!/usr/bin/env bash
# Day 10 虚拟环境一键创建脚本
# 用法：cd day10/code && bash setup_venv.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VENV_DIR="${VENV_DIR:-.venv}"

echo "==> 创建虚拟环境: $VENV_DIR"
python3 -m venv "$VENV_DIR"

echo "==> 激活虚拟环境（当前 shell 需手动 source）"
echo "    source $VENV_DIR/bin/activate"

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

echo "==> 升级 pip"
python -m pip install --upgrade pip

echo "==> 安装 requirements.txt"
pip install -r requirements.txt

echo ""
echo "验收命令："
echo "  python demo_imports.py"
echo "  python demo_exceptions.py"
echo "  python verify_package.py"
echo ""
echo "退出虚拟环境: deactivate"
