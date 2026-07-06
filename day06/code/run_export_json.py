# -*- coding: utf-8 -*-
"""Day 6 入口：员工 JSON 导出（包版）。运行：python3 run_export_json.py"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sparktech_export import build_export_report, export_employees_from_mock


def main() -> None:
    raw, cleaned, output_path = export_employees_from_mock()
    report = build_export_report(raw, cleaned, output_path)
    print(report)
    print(f"\n校验命令: python3 -m json.tool {output_path}")


if __name__ == "__main__":
    main()
