# -*- coding: utf-8 -*-
"""Day 2 字符串方法演示。"""

from __future__ import annotations


def demo_index_slice() -> None:
    s = "SparkTech"
    print(f"s[0]={s[0]}, s[-1]={s[-1]}, s[0:5]={s[0:5]}, s[::-1]={s[::-1]}")


def demo_methods() -> None:
    raw = "  CHENXIAO  "
    print(f"strip: |{raw.strip()}|")
    print(f"lower: {raw.strip().lower()}")
    parts = "a,b,c".split(",")
    print(f"join: {'-'.join(parts)}")


def demo_fstring() -> None:
    name, dept = "陈晓", "大模型应用开发部"
    print(f"【入职】{name} @ {dept}")
    ratio = 0.2567
    print(f"召回率: {ratio:.1%}")


def main() -> None:
    demo_index_slice()
    demo_methods()
    demo_fstring()


if __name__ == "__main__":
    main()
