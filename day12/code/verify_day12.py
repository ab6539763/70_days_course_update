#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Day 12 验收脚本：无 API Key 时验证 mock 模式可运行。"""

from __future__ import annotations

import os
import sys

# 强制 mock：清除可能存在的 Key
os.environ.pop("DEEPSEEK_API_KEY", None)

from llm_client import LLMClient, LLMClientError  # noqa: E402


def check_mock_chat() -> None:
    client = LLMClient()
    assert client.mock_mode, "无 Key 时应为 mock 模式"
    result = client.chat("验收测试")
    assert result.mock is True
    assert "MOCK" in result.content
    print("[OK] LLMClient mock 模式")


def check_messages_format() -> None:
    client = LLMClient()
    messages = client.build_messages("你好", system_message="你是助手")
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    payload = client.build_payload("测试")
    assert payload["model"] == "deepseek-chat"
    assert "messages" in payload
    print("[OK] messages / payload 结构")


def check_empty_prompt() -> None:
    client = LLMClient()
    try:
        client.chat("   ")
        raise AssertionError("空问题应抛错")
    except LLMClientError:
        pass
    print("[OK] 空问题校验")


def main() -> None:
    print("Day 12 verify_day12.py")
    check_messages_format()
    check_mock_chat()
    check_empty_prompt()
    print("\n全部验收通过。")


if __name__ == "__main__":
    main()
