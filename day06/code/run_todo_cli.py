# -*- coding: utf-8 -*-
"""Day 6 入口：待办管理器 CLI（包版）。运行：python3 run_todo_cli.py"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sparktech_todo import run_cli


def main() -> None:
    run_cli()


if __name__ == "__main__":
    main()
