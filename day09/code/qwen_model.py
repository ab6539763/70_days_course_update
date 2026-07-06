"""
Day 9 · 通义千问（Qwen）模型子类

演示：与 OpenAIModel 同接口、不同实现 —— 多态的核心。
"""

from __future__ import annotations

import time
from typing import Any

from base_model import BaseModel, GenerationResult


class QwenModel(BaseModel):
    """阿里云通义千问 mock 实现。"""

    vendor: str = "qwen"

    def __init__(
        self,
        model_name: str = "qwen-plus",
        *,
        api_key: str = "",
        temperature: float = 0.8,
        max_tokens: int = 2048,
        region: str = "cn-beijing",
    ) -> None:
        super().__init__(
            model_name,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        self._region = region

    @property
    def region(self) -> str:
        return self._region

    def build_system_prefix(self) -> str:
        return f"通义千问/{self.model_name}（{self._region}）"

    def generate(self, prompt: str, **kwargs: Any) -> GenerationResult:
        prompt = super()._before_generate(prompt)

        start = time.perf_counter()
        # Qwen mock：中文口吻略有差异，便于课堂对比多态
        reply = (
            f"【{self.build_system_prefix()}】"
            f"模拟回答：关于「{prompt[:40]}{'…' if len(prompt) > 40 else ''}」，"
            f"建议先查阅内部知识库再回复客户。（temperature={self.temperature}）"
        )
        latency_ms = (time.perf_counter() - start) * 1000

        return GenerationResult(
            text=reply,
            model=self.model_name,
            vendor=self.vendor,
            prompt_tokens=max(1, len(prompt) // 3),
            completion_tokens=max(1, len(reply) // 3),
            latency_ms=round(latency_ms, 2),
        )

    def generate_with_search(self, prompt: str, **kwargs: Any) -> GenerationResult:
        """
        Qwen 扩展能力：带「联网搜索」标记的生成（仅子类独有方法）。

        课堂讨论：子类可以新增方法，但对外统一入口仍应是 generate() 或 __call__。
        """
        enriched = f"[enable_search=true] {prompt}"
        result = self.generate(enriched, **kwargs)
        result.text = f"🔍 {result.text}"
        return result
