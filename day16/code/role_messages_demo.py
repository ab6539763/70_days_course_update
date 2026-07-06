# -*- coding: utf-8 -*-
"""
Day 16 · system / user / assistant 角色消息演示

教学目标：
1. 理解三角色在 Chat Completions API 中的分工
2. 对比「有 system」与「无 system」的 mock 回复差异
3. 演示多轮对话 messages 的正确拼装

运行：cd day16/code && python3 role_messages_demo.py
"""

from __future__ import annotations

import json

from llm_compat import get_llm_client, get_day14_client_hint


def build_messages_with_system() -> list[dict[str, str]]:
    """
    推荐结构：system 定义人设，user/assistant 承载多轮历史。
    """
    return [
        {
            "role": "system",
            "content": (
                "你是星火智服官方客服助手。"
                "回答须简洁，不超过 5 句话。"
                "涉及具体工单状态时引导用户提供工单号。"
                "禁止编造退款到账时间。"
            ),
        },
        {"role": "user", "content": "退款一般要多久？"},
        {
            "role": "assistant",
            "content": "一般处理周期为 3–7 个工作日，具体以支付渠道为准。",
        },
        {"role": "user", "content": "我的工单能加急吗？"},
    ]


def build_messages_without_system() -> list[dict[str, str]]:
    """
    反例：把人设塞进 user——多轮后模型容易忽略约束。
    """
    return [
        {
            "role": "user",
            "content": (
                "请你扮演星火智服客服，回答简洁不超过 5 句。"
                "退款一般要多久？"
            ),
        },
    ]


def print_messages_table(messages: list[dict[str, str]]) -> None:
    """打印 messages 结构表。"""
    print(f"{'#':<3} {'role':<12} content 预览")
    print("-" * 60)
    for i, m in enumerate(messages):
        preview = m["content"].replace("\n", " ")[:48]
        if len(m["content"]) > 48:
            preview += "…"
        print(f"{i:<3} {m['role']:<12} {preview}")


def demo_role_structure() -> None:
    print("\n" + "=" * 60)
    print("【1】标准三角色 messages 结构")
    print("=" * 60)
    messages = build_messages_with_system()
    print_messages_table(messages)


def demo_with_vs_without_system() -> None:
    print("\n" + "=" * 60)
    print("【2】有 system vs 无 system（mock 对比）")
    print("=" * 60)

    client = get_llm_client()
    print(f"客户端: {client.client_source} | mode={client.mode}\n")

    for label, messages in [
        ("有 system", build_messages_with_system()),
        ("无 system", build_messages_without_system()),
    ]:
        print(f"── {label} ──")
        resp = client.chat(messages, temperature=0.3, max_tokens=300)
        print(f"回复: {resp.text}\n")


def demo_json_export() -> None:
    """导出 messages JSON，供 Postman / Day 14 会话存储参考。"""
    print("\n" + "=" * 60)
    print("【3】messages JSON（可存入 Day 14 session）")
    print("=" * 60)
    messages = build_messages_with_system()
    print(json.dumps(messages, ensure_ascii=False, indent=2))


def main() -> None:
    print("=" * 60)
    print("Day 16 · role_messages_demo.py")
    print("=" * 60)
    print(get_day14_client_hint())

    demo_role_structure()
    demo_with_vs_without_system()
    demo_json_export()

    print("\n要点:")
    print("  · system 放一次即可，放会话级人设与边界")
    print("  · user/assistant 成对追加，构成多轮历史")
    print("  · Day 14 project1/session.py 维护的即是此列表")
    print("\n✅ role_messages_demo.py 完成")


if __name__ == "__main__":
    main()
