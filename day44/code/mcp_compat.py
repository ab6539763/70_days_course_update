# -*- coding: utf-8 -*-
"""MCP 可用性检测与 mock 回退（Day 44）。"""

from __future__ import annotations

import json
from typing import Any

MCP_AVAILABLE = False
FastMCP = None

try:
    from mcp.server.fastmcp import FastMCP as _FastMCP

    FastMCP = _FastMCP
    MCP_AVAILABLE = True
except ImportError:
    pass


class MockMCPServer:
    """无 mcp SDK 时的最小 JSON-RPC 工具服务。"""

    def __init__(self, name: str = "sparktech-mock-mcp"):
        self.name = name
        self._tools = {
            "kb_search": {
                "description": "搜索星火智服知识库",
                "inputSchema": {
                    "type": "object",
                    "properties": {"query": {"type": "string"}},
                    "required": ["query"],
                },
            },
            "ticket_status": {
                "description": "查询工单状态",
                "inputSchema": {
                    "type": "object",
                    "properties": {"ticket_id": {"type": "string"}},
                    "required": ["ticket_id"],
                },
            },
        }

    def list_tools(self) -> list[dict[str, Any]]:
        return [
            {"name": k, **v}
            for k, v in self._tools.items()
        ]

    def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        if name == "kb_search":
            q = arguments.get("query", "")
            return json.dumps(
                {
                    "hits": [
                        {"title": "退款政策", "snippet": f"与「{q}」相关的退款 7 天规则"},
                        {"title": "API Key", "snippet": "审批 1 个工作日"},
                    ]
                },
                ensure_ascii=False,
            )
        if name == "ticket_status":
            tid = arguments.get("ticket_id", "UNKNOWN")
            return json.dumps({"ticket_id": tid, "status": "处理中", "owner": "张工"}, ensure_ascii=False)
        raise ValueError(f"unknown tool: {name}")


def get_mock_server() -> MockMCPServer:
    return MockMCPServer()
