# -*- coding: utf-8 -*-
"""
Day 46 · Agent 重试与弹性包装器

功能：
- 指数退避重试（可重试 vs 不可重试错误）
- 超时控制
- 简易熔断器
- 与 guardrails 组合

运行：cd day46/code && python3 retry_agent_wrapper.py
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from agent_guardrails import AgentGuardrails


class ErrorKind(str, Enum):
    RETRYABLE = "retryable"
    FATAL = "fatal"


@dataclass
class AgentError(Exception):
    kind: ErrorKind
    message: str

    def __str__(self) -> str:
        return f"[{self.kind.value}] {self.message}"


@dataclass
class RetryConfig:
    max_attempts: int = 3
    base_delay_sec: float = 0.1
    max_delay_sec: float = 2.0
    timeout_sec: float = 30.0


@dataclass
class CircuitBreaker:
    failure_threshold: int = 3
    cooldown_sec: float = 5.0
    _failures: int = 0
    _opened_at: float | None = None

    def record_success(self) -> None:
        self._failures = 0
        self._opened_at = None

    def record_failure(self) -> None:
        self._failures += 1
        if self._failures >= self.failure_threshold:
            self._opened_at = time.monotonic()

    def allow_request(self) -> bool:
        if self._opened_at is None:
            return True
        if time.monotonic() - self._opened_at >= self.cooldown_sec:
            self._failures = 0
            self._opened_at = None
            return True
        return False

    @property
    def is_open(self) -> bool:
        return not self.allow_request()


@dataclass
class RetryStats:
    attempts: int = 0
    total_latency_ms: float = 0.0
    errors: list[str] = field(default_factory=list)


class RetryAgentWrapper:
    """包装任意 agent callable，加重试与护栏。"""

    def __init__(
        self,
        agent_fn: Callable[[str], str],
        *,
        config: RetryConfig | None = None,
        guardrails: AgentGuardrails | None = None,
        breaker: CircuitBreaker | None = None,
    ) -> None:
        self.agent_fn = agent_fn
        self.config = config or RetryConfig()
        self.guardrails = guardrails or AgentGuardrails()
        self.breaker = breaker or CircuitBreaker()
        self.last_stats = RetryStats()

    def _sleep_backoff(self, attempt: int) -> None:
        delay = min(
            self.config.base_delay_sec * (2 ** (attempt - 1)),
            self.config.max_delay_sec,
        )
        time.sleep(delay)

    def invoke(self, user_text: str) -> dict[str, Any]:
        inp = self.guardrails.validate_input(user_text)
        if not inp.allowed:
            return {"ok": False, "stage": "input_guard", "answer": "输入未通过护栏", "reasons": inp.reasons}

        if not self.breaker.allow_request():
            return {"ok": False, "stage": "circuit_open", "answer": "服务暂时不可用，请稍后再试。"}

        stats = RetryStats()
        t0 = time.perf_counter()
        last_err = ""

        for attempt in range(1, self.config.max_attempts + 1):
            stats.attempts = attempt
            try:
                answer = self.agent_fn(inp.text)
                out = self.guardrails.validate_output(answer)
                if not out.allowed:
                    raise AgentError(ErrorKind.FATAL, "output_guard_blocked")
                self.breaker.record_success()
                stats.total_latency_ms = round((time.perf_counter() - t0) * 1000, 2)
                self.last_stats = stats
                return {
                    "ok": True,
                    "answer": out.text,
                    "attempts": attempt,
                    "latency_ms": stats.total_latency_ms,
                }
            except AgentError as exc:
                last_err = str(exc)
                stats.errors.append(last_err)
                if exc.kind == ErrorKind.FATAL:
                    self.breaker.record_failure()
                    break
                if attempt < self.config.max_attempts:
                    self._sleep_backoff(attempt)
            except Exception as exc:  # noqa: BLE001
                last_err = str(exc)
                stats.errors.append(last_err)
                self.breaker.record_failure()
                if attempt < self.config.max_attempts:
                    self._sleep_backoff(attempt)

        stats.total_latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        self.last_stats = stats
        return {
            "ok": False,
            "stage": "retry_exhausted",
            "answer": f"请求失败（已重试 {stats.attempts} 次）：{last_err}",
            "attempts": stats.attempts,
            "errors": stats.errors,
        }


# --- 教学用 flaky agent ---

_call_count = 0


def flaky_agent(query: str) -> str:
    global _call_count
    _call_count += 1
    if _call_count < 3:
        raise AgentError(ErrorKind.RETRYABLE, "upstream_timeout")
    return f"[mock] 成功回答：{query}"


def reset_flaky() -> None:
    global _call_count
    _call_count = 0


def demo() -> None:
    reset_flaky()
    wrapper = RetryAgentWrapper(flaky_agent, config=RetryConfig(max_attempts=4, base_delay_sec=0.05))
    result = wrapper.invoke("查询 SLA")
    print("invoke result:", result)
    print("stats:", wrapper.last_stats)


if __name__ == "__main__":
    demo()
