"""
Day 9 · OpenAI 兼容模型子类

演示：继承 BaseModel、重写 generate()、super() 调用父类钩子。
当前为 mock 实现，不发起真实 HTTP 请求。
"""

from __future__ import annotations

import hashlib
import time
from typing import Any

from base_model import BaseModel, GenerationResult


class OpenAIModel(BaseModel):
    """OpenAI / Azure OpenAI 兼容接口的 mock 实现。"""

    vendor: str = "openai"

    def __init__(
        self,
        model_name: str = "gpt-4o",
        *,
        api_key: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        base_url: str = "https://api.openai.com/v1",
    ) -> None:
        # super() 调用父类 __init__，避免重复写赋值逻辑
        super().__init__(
            model_name,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        self._base_url = base_url

    @property
    def base_url(self) -> str:
        return self._base_url

    def build_system_prefix(self) -> str:
        """重写钩子：OpenAI 风格前缀。"""
        return f"OpenAI/{self.model_name} @ {self._base_url}"

    def generate(self, prompt: str, **kwargs: Any) -> GenerationResult:
        prompt = super()._before_generate(prompt)

        # mock：用 prompt 哈希制造稳定但看似随机的回复
        start = time.perf_counter()
        digest = hashlib.md5(prompt.encode()).hexdigest()[:8]
        reply = (
            f"{self.build_system_prefix()} mock 回复："
            f"已收到「{prompt[:50]}{'…' if len(prompt) > 50 else ''}」。"
            f"（mock_id={digest}）"
        )
        latency_ms = (time.perf_counter() - start) * 1000

        temp = kwargs.get("temperature", self.temperature)
        return GenerationResult(
            text=reply,
            model=self.model_name,
            vendor=self.vendor,
            prompt_tokens=max(1, len(prompt) // 4),
            completion_tokens=max(1, len(reply) // 4),
            latency_ms=round(latency_ms, 2),
        )

    def __repr__(self) -> str:
        # 子类可扩展 repr，仍建议保留 super 信息或调用父类风格
        return (
            f"OpenAIModel(model_name={self.model_name!r}, "
            f"base_url={self.base_url!r}, temperature={self.temperature})"
        )
