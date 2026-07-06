# -*- coding: utf-8 -*-
"""
Day 18 · JSON Mode 与 Function Calling 入门

演示：
1. response_format=json_object 约束结构化输出
2. tools / function calling 声明与 mock 回调

运行：cd day18/code && python3 structured_output_demo.py
"""

from __future__ import annotations

import json
from typing import Any

from llm_client import LLMClient


QUERY_ORDER_TOOL = {
    "type": "function",
    "function": {
        "name": "query_order_status",
        "description": "根据订单号查询物流状态",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "订单号，如 ORD-8821",
                }
            },
            "required": ["order_id"],
        },
    },
}


def mock_query_order_status(order_id: str) -> dict[str, Any]:
    """本地工具实现（Function Calling 回调）。"""
    return {
        "order_id": order_id,
        "status": "运输中",
        "carrier": "中通",
        "last_update": "2026-07-05 18:30",
    }


def demo_json_mode(client: LLMClient) -> dict[str, Any]:
    messages = [
        {
            "role": "system",
            "content": "输出客服工单摘要 JSON，字段：title, priority, tags",
        },
        {
            "role": "user",
            "content": (
                "用户反馈：VIP 客户无法导出会话记录，影响合规审计。"
                "只输出 JSON。"
            ),
        },
    ]
    resp = client.chat(messages, response_format={"type": "json_object"})
    try:
        parsed = json.loads(resp.text)
    except json.JSONDecodeError:
        parsed = {"raw": resp.text}
    return {"mode": resp.mode, "json": parsed}


def demo_function_calling(client: LLMClient) -> dict[str, Any]:
    messages = [
        {
            "role": "system",
            "content": "你是客服助手。需要查订单时请调用 query_order_status 工具。",
        },
        {
            "role": "user",
            "content": "帮我查一下订单 ORD-8821 物流到哪了？",
        },
    ]
    resp = client.chat(messages, tools=[QUERY_ORDER_TOOL], tool_choice="auto")

    tool_result: dict[str, Any] | None = None
    if resp.tool_calls:
        call = resp.tool_calls[0]
        args = json.loads(call["function"]["arguments"])
        tool_result = mock_query_order_status(args["order_id"])

    return {
        "mode": resp.mode,
        "tool_calls": resp.tool_calls,
        "tool_result": tool_result,
        "assistant_text": resp.text,
    }


def main() -> None:
    print("=" * 60)
    print("Day 18 · structured_output_demo.py")
    print("=" * 60)

    client = LLMClient()
    print(f"模式: {client.mode}\n")

    print("### JSON Mode")
    print(json.dumps(demo_json_mode(client), ensure_ascii=False, indent=2))

    print("\n### Function Calling")
    print(json.dumps(demo_function_calling(client), ensure_ascii=False, indent=2))

    print("\n✅ structured_output_demo.py 完成")


if __name__ == "__main__":
    main()
