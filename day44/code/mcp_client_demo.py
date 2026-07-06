# -*- coding: utf-8 -*-
"""
Day 44 · MCP Client 演示

连接 simple_mcp_server 暴露的工具（SDK 或 mock）。
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from mcp_compat import MCP_AVAILABLE
from simple_mcp_server import demo_call_tool, demo_list_tools


@dataclass
class ToolCallResult:
    tool: str
    arguments: dict
    raw: str

    @property
    def parsed(self) -> dict:
        try:
            return json.loads(self.raw)
        except json.JSONDecodeError:
            return {"raw": self.raw}


class SparkTechMCPClient:
    """轻量 MCP 客户端：课堂环境直接调用 demo_call_tool。"""

    def __init__(self):
        self._tools = {t["name"]: t for t in demo_list_tools()}

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())

    def call(self, tool: str, **arguments) -> ToolCallResult:
        if tool not in self._tools:
            raise KeyError(f"tool not found: {tool}")
        raw = demo_call_tool(tool, arguments)
        return ToolCallResult(tool=tool, arguments=arguments, raw=raw)


def run_client_demo() -> dict:
    client = SparkTechMCPClient()
    tools = client.list_tools()
    kb = client.call("kb_search", query="API Key 申请")
    ticket = client.call("ticket_status", ticket_id="INC-2026-042")
    return {
        "sdk": MCP_AVAILABLE,
        "tools": tools,
        "kb_hits": len(kb.parsed.get("hits", [])),
        "ticket_status": ticket.parsed.get("status"),
    }


def main() -> None:
    print("=== Day 44 MCP Client Demo ===\n")
    result = run_client_demo()
    print(f"MCP SDK: {result['sdk']}")
    print(f"tools: {result['tools']}")
    print(f"kb hits: {result['kb_hits']}")
    print(f"ticket status: {result['ticket_status']}")


if __name__ == "__main__":
    main()
