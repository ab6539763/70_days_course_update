# -*- coding: utf-8 -*-
"""
星火科技 · 培训 Day 1
文件：demo_types.py
说明：int / float / str / bool 四类类型的交互演示。

教学目的：
    - 配合讲义 3.2 节，可逐段取消注释观察输出
    - 为 Day 12 阅读 API 响应 JSON 中的类型打基础

运行：python3 demo_types.py
"""

from __future__ import annotations


def demo_integer() -> None:
    """整数：计数、索引。注意 / 与 // 的区别。"""
    token_count = 1024  # 假设某日 API 账单显示消耗 token 数
    print("=== int 整数 ===")
    print(f"token_count = {token_count}, type = {type(token_count)}")
    print(f"整除 // : 1024 // 100 = {1024 // 100}")
    print(f"普通除 / : 1024 / 100 = {1024 / 100}")  # 结果是 float 10.24


def demo_float() -> None:
    """浮点数：temperature 等 API 参数常用 float。"""
    temperature = 0.7  # Day 16 会系统实验此参数
    print("\n=== float 浮点 ===")
    print(f"temperature = {temperature}, type = {type(temperature)}")
    print(f"0.1 + 0.2 = {0.1 + 0.2}")  # 经典浮点精度现象，了解即可


def demo_string() -> None:
    """字符串：姓名、Prompt、JSON 文本在 Python 里都是 str。"""
    role = "user"  # Day 16：API messages 里的 role 字段
    content = "什么是 RAG？"
    print("\n=== str 字符串 ===")
    print(f"单引号与双引号等价：{'ok'}")
    # 三引号可跨行，长 Prompt 常用
    multiline_prompt = """
你是一个企业知识库助手。
请基于给定上下文回答问题。
"""
    print(f"多行 Prompt 长度：{len(multiline_prompt)} 字符")
    # f-string 是后续课程最核心的拼接方式
    message = f'{{"role": "{role}", "content": "{content}"}}'
    print(f"模拟 JSON 片段：{message}")


def demo_bool() -> None:
    """布尔：逻辑判断。注意 True/False 首字母大写。"""
    need_dorm = False
    is_api_ok = True
    print("\n=== bool 布尔 ===")
    print(f"need_dorm = {need_dorm}, type = {type(need_dorm)}")
    print(f"逻辑与：{need_dorm and is_api_ok}")
    print(f"逻辑或：{need_dorm or is_api_ok}")
    # 与信息卡片相关的字符串转布尔
    for raw in ("y", "n", "yes", ""):
        parsed = raw.strip().lower() in ("y", "yes", "是")
        print(f"  输入 {raw!r} -> {parsed}")


def main() -> None:
    print("星火科技 Day1 · 数据类型演示\n")
    demo_integer()
    demo_float()
    demo_string()
    demo_bool()
    print("\n演示结束。")


if __name__ == "__main__":
    main()
