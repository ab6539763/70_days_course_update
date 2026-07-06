#!/usr/bin/env bash
# Day 12 虚拟环境一键创建
# 用法：cd day12/code && bash setup_venv.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VENV_DIR="${VENV_DIR:-.venv}"

echo "==> 创建虚拟环境: $VENV_DIR"
python3 -m venv "$VENV_DIR"

echo "==> 激活虚拟环境"
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

echo "==> 升级 pip"
python -m pip install --upgrade pip

echo "==> 安装 requirements.txt"
pip install -r requirements.txt

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "==> 已复制 .env.example → .env，请填入 DEEPSEEK_API_KEY"
fi

echo ""
echo "验收命令（无需 API Key 亦可 mock 运行）："
echo "  python http_basics_demo.py"
echo "  python llm_client.py"
echo "  python cli_chat_v0.py -q \"你好\""
echo "  python verify_day12.py"
echo ""
echo "配置真实 API：编辑 .env 填入 DEEPSEEK_API_KEY"
echo "退出虚拟环境: deactivate"
