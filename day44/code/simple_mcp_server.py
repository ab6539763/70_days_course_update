# -*- coding: utf-8 -*-
"""
Day 44 · 简易 MCP Server

提供 kb_search / ticket_status 两个工具。
优先使用官方 mcp SDK (FastMCP)；未安装时可用 MockMCPServer 演示协议概念。
"""

from __future__ import annotations

import json
import sys

from mcp_compat import MCP_AVAILABLE, FastMCP, MockMCPServer, get_mock_server


def _kb_search_impl(query: str) -> str:
    return json.dumps(
        {
            "query": query,
            "hits": [
                {"doc": "refund_policy.md", "score": 0.92, "snippet": "7 天内原路退款"},
                {"doc": "api_key_guide.md", "score": 0.81, "snippet": "企业版 API Key 审批流程"},
            ],
        },
        ensure_ascii=False,
    )


def _ticket_status_impl(ticket_id: str) -> str:
    return json.dumps(
        {"ticket_id": ticket_id, "status": "open", "priority": "P2", "assignee": "小陈"},
        ensure_ascii=False,
    )


def build_fastmcp_server():
    if not MCP_AVAILABLE or FastMCP is None:
        raise RuntimeError("mcp SDK 未安装，请使用 run_mock_server()")

    mcp = FastMCP("sparktech-simple-mcp")

    @mcp.tool()
    def kb_search(query: str) -> str:
        """搜索星火智服知识库，返回相关文档片段。"""
        return _kb_search_impl(query)

    @mcp.tool()
    def ticket_status(ticket_id: str) -> str:
        """查询工单当前状态与负责人。"""
        return _ticket_status_impl(ticket_id)

    return mcp


def run_mock_server() -> MockMCPServer:
    """离线/mock 模式：返回内存工具注册表。"""
    return get_mock_server()


def run_stdio_server() -> None:
    """启动 stdio MCP 服务（需 mcp SDK）。"""
    mcp = build_fastmcp_server()
    mcp.run(transport="stdio")


def demo_list_tools() -> list[dict]:
    if MCP_AVAILABLE:
        # FastMCP 工具在运行时注册；mock 列出等价 schema
        mock = run_mock_server()
        return mock.list_tools()
    return run_mock_server().list_tools()


def demo_call_tool(name: str, arguments: dict) -> str:
    if MCP_AVAILABLE:
        if name == "kb_search":
            return _kb_search_impl(arguments.get("query", ""))
        if name == "ticket_status":
            return _ticket_status_impl(arguments.get("ticket_id", ""))
        raise ValueError(name)
    return run_mock_server().call_tool(name, arguments)


def main() -> None:
    print("=== Day 44 Simple MCP Server ===\n")
    print(f"MCP SDK available: {MCP_AVAILABLE}")
    tools = demo_list_tools()
    print(f"tools ({len(tools)}):")
    for t in tools:
        print(f"  - {t['name']}: {t.get('description', '')}")
    sample = demo_call_tool("kb_search", {"query": "退款"})
    print(f"\nkb_search sample:\n{sample}")
    if MCP_AVAILABLE and "--stdio" in sys.argv:
        run_stdio_server()


if __name__ == "__main__":
    main()
