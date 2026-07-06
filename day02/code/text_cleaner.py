# -*- coding: utf-8 -*-
"""Day 2 主程序：文本清洗 CLI。"""

from __future__ import annotations

from constants import MENU_OPTIONS, CaseMode
from cleaners import apply_pipeline, load_sensitive_words


def print_menu() -> None:
    print("\n=== 星火科技 · 文本清洗工具 v1.0 ===\n")
    for key, desc in MENU_OPTIONS.items():
        print(f"  {key}. {desc}")
    print("  多选用逗号分隔，如 1,2,4")


def read_multiline_input() -> str:
    print("\n请输入待清洗文本（单独一行 END 结束）：")
    lines: list[str] = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        lines.append(line)
    return "\n".join(lines)


def parse_options(raw: str) -> dict:
    """解析用户勾选的清洗项。"""
    choices = {c.strip() for c in raw.split(",") if c.strip()}
    case_mode = CaseMode.KEEP
    if "3" in choices:
        print("大小写：1=keep 2=lower 3=upper 4=title")
        cm = input("选择 [1]: ").strip() or "1"
        mapping = {"1": CaseMode.KEEP, "2": CaseMode.LOWER, "3": CaseMode.UPPER, "4": CaseMode.TITLE}
        case_mode = mapping.get(cm, CaseMode.KEEP)
    return {
        "do_strip": "1" in choices,
        "do_collapse": "2" in choices,
        "do_remove_all": "5" in choices,
        "case_mode": case_mode,
        "do_mask": "4" in choices,
        "sensitive_words": load_sensitive_words(),
    }


def format_report(before: str, after: str) -> str:
    width = 52
    reduced = len(before) - len(after)
    return f"""
{"=" * width}
清洗前（{len(before)} 字符）：
{before}
{"-" * width}
清洗后（{len(after)} 字符，减少 {reduced} 字符）：
{after}
{"=" * width}
"""


def main() -> None:
    print_menu()
    while True:
        opts_raw = input("\n请选择清洗项（回车默认 1,2）: ").strip() or "1,2"
        options = parse_options(opts_raw)
        text = read_multiline_input()
        if not text:
            print("未输入内容，跳过。")
        else:
            cleaned = apply_pipeline(text, **options)
            print(format_report(text, cleaned))
        cont = input("继续处理？(y/n) [n]: ").strip().lower()
        if cont not in ("y", "yes", "是"):
            print("再见。")
            break


if __name__ == "__main__":
    main()
