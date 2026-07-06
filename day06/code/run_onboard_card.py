# -*- coding: utf-8 -*-
"""Day 6 入口：入职信息卡片（包版）。运行：python3 run_onboard_card.py"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sparktech_onboard import collect_inputs, render_card


def main() -> None:
    card = collect_inputs()
    print()
    print(render_card(card))


if __name__ == "__main__":
    main()
