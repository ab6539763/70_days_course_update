"""
Day 9 · 星火智服 · LLM 统一接口基类

业务背景：星火智服需要对接 OpenAI、通义千问等多家厂商。
BaseModel 定义「所有模型都必须遵守」的契约，子类通过继承 + 方法重写实现差异。

上午知识点：继承、多态、方法重写、super()
下午知识点：__str__、__repr__、__call__、@property
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class GenerationResult:
    """一次 generate 调用的结构化返回（便于日后接真实 API）。"""

    text: str
    model: str
    vendor: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_ms: float = 0.0
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return (
            f"GenerationResult(model={self.model!r}, vendor={self.vendor!r}, "
            f"text={self.text[:40]!r}...)"
        )


class BaseModel:
    """
    LLM 抽象基类（abstract-ish）。

    不强制继承 abc.ABC，但子类必须重写 generate()，否则调用时抛出 NotImplementedError。
    这符合培训阶段「先理解概念、再引入标准库 ABC」的节奏。
    """

    vendor: str = "unknown"

    def __init__(
        self,
        model_name: str,
        *,
        api_key: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> None:
        self._model_name = model_name
        self._api_key = api_key
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._call_count = 0

    # ------------------------------------------------------------------
    # @property：对外只读暴露配置，避免调用方直接改内部状态
    # ------------------------------------------------------------------

    @property
    def model_name(self) -> str:
        """模型标识，如 gpt-4o、qwen-plus。"""
        return self._model_name

    @property
    def temperature(self) -> float:
        return self._temperature

    @temperature.setter
    def temperature(self, value: float) -> None:
        if not 0.0 <= value <= 2.0:
            raise ValueError("temperature 必须在 0.0～2.0 之间")
        self._temperature = value

    @property
    def max_tokens(self) -> int:
        return self._max_tokens

    @property
    def call_count(self) -> int:
        """累计调用次数（演示 @property 只读统计）。"""
        return self._call_count

    @property
    def is_configured(self) -> bool:
        """是否已配置 API Key（mock 阶段可为空）。"""
        return bool(self._api_key)

    # ------------------------------------------------------------------
    # 核心业务方法：子类必须重写
    # ------------------------------------------------------------------

    def generate(self, prompt: str, **kwargs: Any) -> GenerationResult:
        """
        根据用户 prompt 生成回复。

        子类应重写此方法，并在开头调用 super()._before_generate(prompt) 以复用计数逻辑。
        """
        raise NotImplementedError(
            f"{type(self).__name__} 必须实现 generate() 方法"
        )

    def _before_generate(self, prompt: str) -> str:
        """模板方法：子类在 generate 开头可调用，统一做校验与计数。"""
        cleaned = prompt.strip()
        if not cleaned:
            raise ValueError("prompt 不能为空")
        self._call_count += 1
        return cleaned

    def build_system_prefix(self) -> str:
        """钩子方法：子类可重写以注入厂商专属 system 前缀。"""
        return f"[{self.vendor}/{self.model_name}]"

    # ------------------------------------------------------------------
    # 魔术方法
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        """面向终端用户的简短描述（print(model) 时调用）。"""
        key_hint = "已配置" if self.is_configured else "未配置 Key"
        return (
            f"{self.vendor} 模型 {self.model_name} "
            f"(temp={self.temperature}, {key_hint})"
        )

    def __repr__(self) -> str:
        """面向开发者调试的精确描述（交互式解释器默认显示）。"""
        return (
            f"{type(self).__name__}("
            f"model_name={self.model_name!r}, "
            f"temperature={self.temperature}, "
            f"max_tokens={self.max_tokens})"
        )

    def __call__(self, prompt: str, **kwargs: Any) -> GenerationResult:
        """
        让实例像函数一样可调用：model("你好") 等价于 model.generate("你好")。

        LangChain 等框架里 Runnable 也常用 __call__ 统一调用入口。
        """
        return self.generate(prompt, **kwargs)
