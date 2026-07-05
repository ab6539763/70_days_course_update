#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day 12 · LLMClient — 星火智服首次 DeepSeek API 封装

- 从环境变量读取 DEEPSEEK_API_KEY / DEEPSEEK_BASE_URL
- 无 API Key 时进入 mock 模式：打印将发送的请求，返回模拟回复
- 绝不硬编码密钥
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from typing import Any

import requests

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None  # type: ignore[assignment,misc]


DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-chat"
CHAT_PATH = "/v1/chat/completions"
TIMEOUT = 60


@dataclass
class ChatResponse:
    """解析后的对话响应。"""

    content: str
    model: str
    usage: dict[str, int]
    raw: dict[str, Any]
    mock: bool = False


class LLMClientError(Exception):
    """LLM 调用相关错误。"""


class LLMClient:
    """
    DeepSeek Chat Completions 轻量客户端（OpenAI 兼容格式）。

    环境变量：
        DEEPSEEK_API_KEY   — API 密钥，缺失则 mock 模式
        DEEPSEEK_BASE_URL  — 默认 https://api.deepseek.com
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str = DEFAULT_MODEL,
    ) -> None:
        if load_dotenv is not None:
            load_dotenv()

        self.api_key = (api_key if api_key is not None else os.getenv("DEEPSEEK_API_KEY", "")).strip()
        raw_base = base_url if base_url is not None else os.getenv("DEEPSEEK_BASE_URL", DEFAULT_BASE_URL)
        self.base_url = raw_base.rstrip("/")
        self.model = model
        self.mock_mode = not self.api_key

    @property
    def endpoint(self) -> str:
        return f"{self.base_url}{CHAT_PATH}"

    def build_messages(
        self,
        user_message: str,
        *,
        system_message: str | None = None,
    ) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": user_message})
        return messages

    def build_payload(
        self,
        user_message: str,
        *,
        system_message: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> dict[str, Any]:
        return {
            "model": self.model,
            "messages": self.build_messages(user_message, system_message=system_message),
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

    def build_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _print_mock_request(self, payload: dict[str, Any]) -> None:
        """Mock 模式：展示即将发送的 HTTP 请求（Key 脱敏）。"""
        print("\n[MOCK 模式] 未检测到 DEEPSEEK_API_KEY，不会发起真实网络请求。")
        print("以下是将发送的请求内容：")
        print(f"  POST {self.endpoint}")
        print(f"  Headers: {json.dumps(self._masked_headers(), ensure_ascii=False)}")
        print(f"  Body: {json.dumps(payload, ensure_ascii=False, indent=2)}")
        print()

    def _masked_headers(self) -> dict[str, str]:
        if not self.api_key:
            return {"Authorization": "Bearer <未设置>", "Content-Type": "application/json"}
        masked = self.api_key[:4] + "****" if len(self.api_key) > 4 else "****"
        return {"Authorization": f"Bearer {masked}", "Content-Type": "application/json"}

    def _mock_chat(self, payload: dict[str, Any]) -> ChatResponse:
        self._print_mock_request(payload)
        user_text = payload["messages"][-1]["content"]
        reply = (
            f"[MOCK 回复] 星火智服已收到您的问题：「{user_text}」。"
            "配置 DEEPSEEK_API_KEY 后将返回真实模型回答。"
        )
        return ChatResponse(
            content=reply,
            model=self.model,
            usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            raw={"mock": True},
            mock=True,
        )

    def _real_chat(self, payload: dict[str, Any]) -> ChatResponse:
        try:
            response = requests.post(
                self.endpoint,
                headers=self.build_headers(),
                json=payload,
                timeout=TIMEOUT,
            )
        except requests.RequestException as exc:
            raise LLMClientError(f"网络请求失败: {exc}") from exc

        if response.status_code == 401:
            raise LLMClientError("API Key 无效或未授权（401）")
        if response.status_code == 429:
            raise LLMClientError("请求过于频繁，请稍后重试（429）")
        if not response.ok:
            raise LLMClientError(
                f"API 返回错误: HTTP {response.status_code} — {response.text[:300]}"
            )

        try:
            data: dict[str, Any] = response.json()
        except json.JSONDecodeError as exc:
            raise LLMClientError("响应不是合法 JSON") from exc

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMClientError(f"无法解析响应结构: {json.dumps(data, ensure_ascii=False)[:200]}") from exc

        usage = data.get("usage") or {}
        return ChatResponse(
            content=content.strip(),
            model=data.get("model", self.model),
            usage={
                "prompt_tokens": int(usage.get("prompt_tokens", 0)),
                "completion_tokens": int(usage.get("completion_tokens", 0)),
                "total_tokens": int(usage.get("total_tokens", 0)),
            },
            raw=data,
            mock=False,
        )

    def chat(
        self,
        user_message: str,
        *,
        system_message: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> ChatResponse:
        """
        单轮对话：发送 user（可选 system）消息，返回模型回复。

        无 API Key 时进入 mock 模式，打印请求并返回模拟文本。
        """
        user_message = user_message.strip()
        if not user_message:
            raise LLMClientError("user_message 不能为空")

        payload = self.build_payload(
            user_message,
            system_message=system_message,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        if self.mock_mode:
            return self._mock_chat(payload)
        return self._real_chat(payload)


def main() -> None:
    """命令行快速验证：python llm_client.py \"你好\""""

    prompt = " ".join(sys.argv[1:]) or "星火智服第一次调用 DeepSeek，请用一句话自我介绍。"
    client = LLMClient()
    mode = "MOCK" if client.mock_mode else "LIVE"
    print(f"LLMClient 模式: {mode} | 模型: {client.model}")

    try:
        result = client.chat(
            prompt,
            system_message="你是星火智服的企业客服助手，回答简洁专业。",
        )
    except LLMClientError as exc:
        print(f"错误: {exc}", file=sys.stderr)
        sys.exit(1)

    print("\n--- 模型回复 ---")
    print(result.content)
    if not result.mock:
        print(f"\n[用量] prompt={result.usage['prompt_tokens']}, "
              f"completion={result.usage['completion_tokens']}, "
              f"total={result.usage['total_tokens']}")


if __name__ == "__main__":
    main()
