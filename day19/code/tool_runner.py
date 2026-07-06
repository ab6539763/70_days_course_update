# -*- coding: utf-8 -*-
"""
Day 19 · 工具调用执行器

解析模型返回的 tool_calls，路由到 tools.py 中的实现，并格式化为
OpenAI 兼容的 tool 消息供下一轮对话使用。
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from tools import TOOL_REGISTRY, ToolError


@dataclass
class ToolCallResult:
    """单次工具调用执行结果。"""

    tool_call_id: str
    name: str
    arguments: dict[str, Any]
    success: bool
    output: Any
    error: str | None = None

    def to_tool_message(self) -> dict[str, Any]:
        """转为 chat messages 中的 role=tool 消息。"""
        content = json.dumps(self.output, ensure_ascii=False) if self.success else self.error or ""
        return {
            "role": "tool",
            "tool_call_id": self.tool_call_id,
            "name": self.name,
            "content": content,
        }


@dataclass
class ToolRunReport:
    """一批 tool_calls 的执行报告。"""

    results: list[ToolCallResult] = field(default_factory=list)

    @property
    def tool_messages(self) -> list[dict[str, Any]]:
        return [r.to_tool_message() for r in self.results]

    @property
    def all_success(self) -> bool:
        return all(r.success for r in self.results)


def parse_arguments(raw: str | dict[str, Any]) -> dict[str, Any]:
    """解析模型返回的 arguments（JSON 字符串或 dict）。"""
    if isinstance(raw, dict):
        return raw
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ToolError(f"arguments JSON 解析失败: {exc}") from exc


def execute_tool(name: str, arguments: dict[str, Any]) -> Any:
    """按名称调用注册工具。"""
    func = TOOL_REGISTRY.get(name)
    if func is None:
        raise ToolError(f"未注册的工具: {name}")
    return func(**arguments)


def run_tool_call(tool_call: dict[str, Any]) -> ToolCallResult:
    """
    执行单个 tool_call 对象。

    期望格式（OpenAI 兼容）：
    {
        "id": "call_xxx",
        "type": "function",
        "function": {"name": "get_weather", "arguments": "{...}"}
    }
    """
    call_id = tool_call.get("id", "call_unknown")
    func_block = tool_call.get("function") or {}
    name = func_block.get("name", "")
    raw_args = func_block.get("arguments", "{}")

    try:
        args = parse_arguments(raw_args)
        output = execute_tool(name, args)
        return ToolCallResult(
            tool_call_id=call_id,
            name=name,
            arguments=args,
            success=True,
            output=output,
        )
    except (ToolError, TypeError, ValueError) as exc:
        return ToolCallResult(
            tool_call_id=call_id,
            name=name,
            arguments=parse_arguments(raw_args) if isinstance(raw_args, dict) else {},
            success=False,
            output=None,
            error=str(exc),
        )


def run_tool_calls(tool_calls: list[dict[str, Any]]) -> ToolRunReport:
    """批量执行 tool_calls。"""
    report = ToolRunReport()
    for call in tool_calls:
        report.results.append(run_tool_call(call))
    return report


def main() -> None:
    print("=" * 60)
    print("Day 19 · tool_runner.py 演示")
    print("=" * 60)

    sample_calls = [
        {
            "id": "call_weather_1",
            "type": "function",
            "function": {
                "name": "get_weather",
                "arguments": json.dumps({"city": "上海"}, ensure_ascii=False),
            },
        },
        {
            "id": "call_calc_1",
            "type": "function",
            "function": {
                "name": "calculate",
                "arguments": '{"expression": "2 ** 10"}',
            },
        },
        {
            "id": "call_db_1",
            "type": "function",
            "function": {
                "name": "query_products",
                "arguments": json.dumps({"keyword": "embedding"}, ensure_ascii=False),
            },
        },
    ]

    report = run_tool_calls(sample_calls)
    for result in report.results:
        status = "OK" if result.success else "FAIL"
        print(f"\n[{status}] {result.name}({result.arguments})")
        if result.success:
            print(json.dumps(result.output, ensure_ascii=False, indent=2))
        else:
            print(f"  错误: {result.error}")

    print("\n--- tool messages ---")
    for msg in report.tool_messages:
        print(json.dumps(msg, ensure_ascii=False))

    print("\n✅ tool_runner.py 完成")


if __name__ == "__main__":
    main()
