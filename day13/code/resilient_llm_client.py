# -*- coding: utf-8 -*-
"""
Day 13 · 弹性 LLM 客户端

在 Day 12 llm_client 基础上叠加：
- @retry：对 5xx / 网络抖动自动重试
- @timeout：单次 HTTP 硬超时
- dotenv 加固：启动时校验 Key 格式（mock 模式除外）

运行：cd day13/code && python3 resilient_llm_client.py
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

CODE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE_DIR))

from api_decorators import APIRetryExhaustedError, APITimeoutError, retry, timeout
from llm_client import (
    ChatResponse,
    LLMClient,
    LLMHTTPError,
    load_dotenv_file,
    resolve_api_key,
)


# 仅对这些异常重试（4xx 业务错误不重试）
RETRYABLE_EXCEPTIONS = (LLMHTTPError, ConnectionError, TimeoutError)


class ResilientLLMClient(LLMClient):
    """
    生产级弹性客户端：继承 Day 12 LLMClient，只增强 _live_chat。

    mock 模式不走装饰器，保证课堂无 Key 时秒级响应。
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 0.5,
    ) -> None:
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            model=model,
            timeout=timeout,
        )
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self._validate_config()

    def _validate_config(self) -> None:
        """dotenv 加固：live 模式下 Key 不能为空且格式合理。"""
        if self.is_mock_mode:
            print("[config] 未检测到 OPENAI_API_KEY → mock 模式")
            return
        key = self._api_key
        if len(key) < 8:
            raise ValueError("OPENAI_API_KEY 过短，请检查 .env")
        masked = f"{key[:4]}****{key[-4:]}" if len(key) > 8 else "****"
        print(f"[config] live 模式 | Key={masked} | model={self.model}")

    def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> ChatResponse:
        if self.is_mock_mode:
            return super().chat(messages, **kwargs)
        return self._resilient_live_chat(messages, **kwargs)

    def _resilient_live_chat(
        self, messages: list[dict[str, str]], **kwargs: Any
    ) -> ChatResponse:
        """对 _live_chat 应用 retry + timeout 装饰器（运行时绑定）。"""

        @timeout(kwargs.get("timeout", self._timeout))
        @retry(
            max_attempts=self._max_retries,
            delay=self._retry_delay,
            exceptions=RETRYABLE_EXCEPTIONS,
        )
        def _call() -> ChatResponse:
            return self._live_chat(messages, **kwargs)

        return _call()


class SimulatedFlakyClient(ResilientLLMClient):
    """
    教学用：模拟生产环境间歇性 503，验证 retry 生效。
    继承 ResilientLLMClient，覆盖 _live_chat 注入故障。
    """

    def __init__(self, fail_times: int = 2, **kwargs: Any) -> None:
        # 强制 mock 路径关闭，用假 Key 走 live 分支
        super().__init__(api_key="sk-test-flaky-demo-key", **kwargs)
        self._fail_times = fail_times
        self._call_count = 0

    def _live_chat(self, messages: list[dict[str, str]], **kwargs: Any) -> ChatResponse:
        self._call_count += 1
        if self._call_count <= self._fail_times:
            raise LLMHTTPError(
                f"模拟 503 Service Unavailable（第 {self._call_count} 次）",
                status_code=503,
            )
        user_text = next(
            (m["content"] for m in reversed(messages) if m.get("role") == "user"),
            "",
        )
        return ChatResponse(
            text=f"[recovered] 第 {self._call_count} 次调用成功：{user_text[:40]}",
            model=self.model,
            mode="live",
            latency_ms=1.0,
            prompt_tokens=10,
            completion_tokens=20,
            raw={"recovered_after": self._call_count},
        )

    def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> ChatResponse:
        @timeout(kwargs.get("timeout", self._timeout))
        @retry(
            max_attempts=self._max_retries,
            delay=self._retry_delay,
            exceptions=RETRYABLE_EXCEPTIONS,
        )
        def _call() -> ChatResponse:
            return self._live_chat(messages, **kwargs)

        return _call()


def demo_mock_mode() -> None:
    print("\n--- 1. mock 模式（无 API Key）---")
    client = ResilientLLMClient()
    result = client.chat([{"role": "user", "content": "Day 13 弹性客户端验收"}])
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))


def demo_flaky_retry() -> None:
    print("\n--- 2. 模拟 503 + retry 恢复 ---")
    client = SimulatedFlakyClient(fail_times=2, max_retries=4, retry_delay=0.1)
    result = client.chat([{"role": "user", "content": "retry 测试"}])
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))


def demo_timeout() -> None:
    print("\n--- 3. timeout 演示 ---")

    class SlowClient(ResilientLLMClient):
        """教学用：慢响应触发 timeout，不发起真实 HTTP。"""

        def __init__(self, **kwargs: Any) -> None:
            super().__init__(api_key="sk-test-timeout-demo", **kwargs)

        def _live_chat(self, messages, **kwargs):
            time.sleep(2.0)
            return ChatResponse(text="不应出现", model=self.model, mode="live")

    client = SlowClient(timeout=0.5, max_retries=1)
    try:
        client.chat([{"role": "user", "content": "慢调用"}])
    except APITimeoutError as exc:
        print(f"捕获超时: {exc}")


def main() -> None:
    print("=" * 60)
    print("Day 13 · resilient_llm_client.py")
    print("=" * 60)
    load_dotenv_file()
    demo_mock_mode()
    demo_flaky_retry()
    demo_timeout()
    print("\n✅ resilient_llm_client.py 完成")


if __name__ == "__main__":
    main()
