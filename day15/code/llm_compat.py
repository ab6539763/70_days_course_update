# -*- coding: utf-8 -*-
"""
Day 15 · 衔接 Day 12–14 LLM 客户端

按优先级尝试导入：
1. day13/code/resilient_llm_client.py → ResilientLLMClient
2. day13/code/llm_client.py → LLMClient
3. day12/code/llm_client.py → LLMClient（DeepSeek 路径）

无 API Key 时各客户端均进入 mock 模式，培训环境友好。

运行：cd day15/code && python3 llm_compat.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Protocol

WORKSPACE = Path(__file__).resolve().parents[2]
DAY12_CODE = WORKSPACE / "day12" / "code"
DAY13_CODE = WORKSPACE / "day13" / "code"
DAY14_ROOT = WORKSPACE / "day14"

CLIENT_SOURCE = "builtin-fallback"


class ChatClientProtocol(Protocol):
    """统一 chat 接口，兼容 Day 12/13 返回结构。"""

    @property
    def mode(self) -> str: ...

    @property
    def model(self) -> str: ...

    def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> Any: ...


class _FallbackChatResponse:
    """极端降级：前序课程目录缺失时的本地 mock。"""

    def __init__(self, text: str, model: str = "mock-local") -> None:
        self.text = text
        self.model = model
        self.mode = "mock"
        self.prompt_tokens = max(1, len(text) // 4)
        self.completion_tokens = 20
        self.latency_ms = 1.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "model": self.model,
            "mode": self.mode,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
        }


class _FallbackLLMClient:
    """内置最小客户端，保证 verify 在无 day12/13 时仍可通过。"""

    def __init__(self) -> None:
        self._model = "gpt-4o-mini"

    @property
    def mode(self) -> str:
        return "mock"

    @property
    def model(self) -> str:
        return self._model

    def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> _FallbackChatResponse:
        user = next(
            (m["content"] for m in reversed(messages) if m.get("role") == "user"),
            "",
        )
        return _FallbackChatResponse(
            f"[fallback-mock] 收到：{user[:40]}",
            model=self._model,
        )


def _ensure_path(path: Path) -> None:
    s = str(path)
    if path.is_dir() and s not in sys.path:
        sys.path.insert(0, s)


def get_llm_client(**kwargs: Any) -> ChatClientProtocol:
    """
    获取 LLM 客户端实例。

    Returns:
        具备 chat(messages) 与 mode/model 属性的客户端。
    """
    global CLIENT_SOURCE

    # 优先 Day 13 弹性客户端
    if DAY13_CODE.is_dir():
        _ensure_path(DAY13_CODE)
        try:
            from resilient_llm_client import ResilientLLMClient

            CLIENT_SOURCE = "day13/resilient_llm_client.py"
            return ResilientLLMClient(**kwargs)
        except ImportError:
            try:
                from llm_client import LLMClient

                CLIENT_SOURCE = "day13/llm_client.py"
                return LLMClient(**kwargs)
            except ImportError:
                pass

    # 回退 Day 12
    if DAY12_CODE.is_dir():
        _ensure_path(DAY12_CODE)
        try:
            from llm_client import LLMClient

            CLIENT_SOURCE = "day12/llm_client.py"
            return LLMClient(**kwargs)
        except ImportError:
            pass

    CLIENT_SOURCE = "day15/llm_compat.py (_FallbackLLMClient)"
    return _FallbackLLMClient()


def get_day14_client_hint() -> str:
    """返回 Day 14 项目客户端说明（不强制 import，避免 openai 依赖）。"""
    llm_path = DAY14_ROOT / "project1" / "llm_client.py"
    if llm_path.is_file():
        return (
            f"Day 14 多轮助手客户端: {llm_path}\n"
            "  - mock: 无 OPENAI_API_KEY 或 SPARKTECH_MOCK=1\n"
            "  - live: 配置 Key 后 OpenAI SDK 调用"
        )
    return "Day 14 project1/llm_client.py 未找到"


def main() -> None:
    print("=" * 60)
    print("Day 15 · llm_compat · Day 12–14 客户端桥接")
    print("=" * 60)

    client = get_llm_client()
    print(f"来源: {CLIENT_SOURCE}")
    print(f"模式: {client.mode} | 模型: {client.model}")
    print()
    print(get_day14_client_hint())
    print()

    messages = [{"role": "user", "content": "用一句话说明 Token 计费。"}]
    resp = client.chat(messages)
    if hasattr(resp, "to_dict"):
        import json

        print(json.dumps(resp.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(resp)
    print("\n✅ llm_compat.py 完成")


if __name__ == "__main__":
    main()
