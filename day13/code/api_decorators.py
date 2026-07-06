# -*- coding: utf-8 -*-
"""
Day 13 · API 装饰器：重试与超时控制

为 LLM HTTP 调用提供可组合的装饰器：
- @retry：指数退避重试，可配置异常类型
- @timeout：限制单次调用最长等待时间

运行：cd day13/code && python3 api_decorators.py
"""

from __future__ import annotations

import functools
import random
import time
from collections.abc import Callable, Iterable
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from typing import Any, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


class APITimeoutError(TimeoutError):
    """API 调用超过装饰器设定的超时时间。"""

    def __init__(self, seconds: float, func_name: str) -> None:
        self.seconds = seconds
        self.func_name = func_name
        super().__init__(f"{func_name} 超时（>{seconds}s）")


class APIRetryExhaustedError(RuntimeError):
    """重试次数用尽后仍失败。"""

    def __init__(self, attempts: int, last_error: BaseException) -> None:
        self.attempts = attempts
        self.last_error = last_error
        super().__init__(f"重试 {attempts} 次后仍失败: {last_error}")


def retry(
    *,
    max_attempts: int = 3,
    delay: float = 0.5,
    backoff: float = 2.0,
    jitter: float = 0.1,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    重试装饰器（带指数退避）。

    Args:
        max_attempts: 最多尝试次数（含首次）
        delay: 首次重试前等待秒数
        backoff: 每次重试 delay 的乘数
        jitter: 随机抖动上限，避免惊群
        exceptions: 触发重试的异常类型元组
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            wait = delay
            last_exc: BaseException | None = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc
                    if attempt >= max_attempts:
                        break
                    sleep_for = wait + random.uniform(0, jitter)
                    print(
                        f"[retry] {func.__name__} 第 {attempt}/{max_attempts} 次失败: "
                        f"{exc!r}，{sleep_for:.2f}s 后重试"
                    )
                    time.sleep(sleep_for)
                    wait *= backoff

            assert last_exc is not None
            raise APIRetryExhaustedError(max_attempts, last_exc) from last_exc

        return wrapper

    return decorator


def timeout(seconds: float) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    超时装饰器（基于 ThreadPoolExecutor，跨平台可用）。

    注意：被装饰函数会在独立线程中执行；若函数持有不可跨线程资源需慎用。
  """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            with ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(func, *args, **kwargs)
                try:
                    return future.result(timeout=seconds)
                except FuturesTimeoutError as exc:
                    raise APITimeoutError(seconds, func.__name__) from exc

        return wrapper

    return decorator


def log_calls(label: str = "") -> Callable[[Callable[P, R]], Callable[P, R]]:
    """教学用：打印函数调用信息（演示装饰器可叠加）。"""

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        tag = label or func.__name__

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            print(f"[log] 调用 {tag} args={args!r} kwargs={kwargs!r}")
            result = func(*args, **kwargs)
            print(f"[log] 返回 {tag} -> {result!r}")
            return result

        return wrapper

    return decorator


# ---------------------------------------------------------------------------
# 教学演示
# ---------------------------------------------------------------------------

_attempt_counter = 0


@retry(max_attempts=3, delay=0.2, exceptions=(ConnectionError,))
def flaky_network_call(url: str) -> str:
    """模拟不稳定网络：前两次 ConnectionError，第三次成功。"""
    global _attempt_counter
    _attempt_counter += 1
    if _attempt_counter < 3:
        raise ConnectionError(f"模拟断连 #{_attempt_counter}: {url}")
    return f"OK from {url}"


@timeout(0.3)
def slow_api(seconds: float) -> str:
    """模拟慢 API，用于触发超时。"""
    time.sleep(seconds)
    return "done"


def demo_retry() -> None:
    global _attempt_counter
    _attempt_counter = 0
    print("\n--- retry 演示 ---")
    result = flaky_network_call("https://api.sparktech.local/v1/chat")
    print(f"最终结果: {result}")


def demo_timeout() -> None:
    print("\n--- timeout 演示 ---")
    try:
        slow_api(1.0)
    except APITimeoutError as exc:
        print(f"捕获超时: {exc}")


def demo_stack() -> None:
    """演示装饰器叠加：timeout 在外层，retry 在内层。"""

    @timeout(2.0)
    @retry(max_attempts=2, delay=0.1, exceptions=(ValueError,))
    def nested() -> str:
        return "stacked ok"

    print("\n--- 装饰器叠加 ---")
    print(nested())


def main() -> None:
    print("=" * 60)
    print("Day 13 · api_decorators.py")
    print("=" * 60)
    demo_retry()
    demo_timeout()
    demo_stack()
    print("\n✅ api_decorators.py 完成")


if __name__ == "__main__":
    main()
