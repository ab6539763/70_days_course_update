# -*- coding: utf-8 -*-
"""
Day 13 上午 · 装饰器原理与应用

覆盖：
- 函数装饰器、@语法糖、functools.wraps
- 带参数装饰器
- 类装饰器入门
- 实战：计时、日志、权限检查

运行：cd day13/code && python3 decorator_demo.py
"""

from __future__ import annotations

import functools
import time
from collections.abc import Callable
from typing import Any, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


# ---------------------------------------------------------------------------
# 第一章：最简装饰器
# ---------------------------------------------------------------------------


def simple_logger(func: Callable[P, R]) -> Callable[P, R]:
    """无参装饰器：在调用前后打印日志。"""

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"[simple_logger] 进入 {func.__name__}")
        result = func(*args, **kwargs)
        print(f"[simple_logger] 离开 {func.__name__} -> {result!r}")
        return result

    return wrapper


@simple_logger
def add(a: int, b: int) -> int:
    """两数相加。"""
    return a + b


# ---------------------------------------------------------------------------
# 第二章：带参数的装饰器（三层嵌套）
# ---------------------------------------------------------------------------


def repeat(times: int) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """重复执行被装饰函数 times 次，返回最后一次结果。"""

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last: R | None = None
            for i in range(times):
                print(f"[repeat] 第 {i + 1}/{times} 次")
                last = func(*args, **kwargs)
            assert last is not None
            return last

        return wrapper

    return decorator


@repeat(times=2)
def greet(name: str) -> str:
    return f"你好，{name}！"


# ---------------------------------------------------------------------------
# 第三章：计时装饰器（LLM 调用必备）
# ---------------------------------------------------------------------------


def timing(func: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed_ms = (time.perf_counter() - start) * 1000
        print(f"[timing] {func.__name__} 耗时 {elapsed_ms:.2f} ms")
        return result

    return wrapper


@timing
def slow_compute(n: int) -> int:
    """模拟耗时计算。"""
    total = 0
    for i in range(n):
        total += i
    return total


# ---------------------------------------------------------------------------
# 第四章：权限检查（业务场景）
# ---------------------------------------------------------------------------


def require_role(*roles: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """仅允许指定角色调用（演示闭包保存 roles）。"""

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            current_role = kwargs.pop("_role", "guest")
            if current_role not in roles:
                raise PermissionError(f"需要角色 {roles}，当前为 {current_role!r}")
            return func(*args, **kwargs)

        return wrapper

    return decorator


@require_role("admin", "ops")
def delete_ticket(ticket_id: str) -> str:
    return f"已删除工单 {ticket_id}"


# ---------------------------------------------------------------------------
# 第五章：类装饰器
# ---------------------------------------------------------------------------


def singleton(cls: type) -> type:
    """保证类只实例化一次（简化版单例）。"""
    instances: dict[type, object] = {}

    @functools.wraps(cls, updated=())
    def get_instance(*args: Any, **kwargs: Any) -> object:
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance  # type: ignore[return-value]


@singleton
class ConfigRegistry:
    def __init__(self) -> None:
        self.settings: dict[str, str] = {}

    def set(self, key: str, value: str) -> None:
        self.settings[key] = value


# ---------------------------------------------------------------------------
# 第六章：装饰器本质 —— 等价于 func = decorator(func)
# ---------------------------------------------------------------------------


def plain_multiply(x: int, y: int) -> int:
    return x * y


decorated_multiply = timing(plain_multiply)


def demo_equivalence() -> None:
    print("\n--- 装饰器等价写法 ---")
    print(f"add.__name__ = {add.__name__}")  # functools.wraps 保留原名
    print(f"plain_multiply(3,4) = {plain_multiply(3, 4)}")
    print(f"decorated_multiply(3,4) = {decorated_multiply(3, 4)}")


def main() -> None:
    print("=" * 60)
    print("Day 13 上午 · decorator_demo.py")
    print("=" * 60)

    print("\n--- §1 基础装饰器 ---")
    print(add(2, 3))

    print("\n--- §2 带参装饰器 ---")
    print(greet("星火培训生"))

    print("\n--- §3 计时 ---")
    print(slow_compute(100_000))

    print("\n--- §4 权限检查 ---")
    try:
        delete_ticket("T-001", _role="guest")
    except PermissionError as exc:
        print(f"拒绝: {exc}")
    print(delete_ticket("T-001", _role="admin"))

    print("\n--- §5 类装饰器 singleton ---")
    a = ConfigRegistry()
    b = ConfigRegistry()
    a.set("env", "production")
    print(f"同一实例: {a is b}, settings={b.settings}")

    demo_equivalence()
    print("\n✅ decorator_demo.py 完成")


if __name__ == "__main__":
    main()
