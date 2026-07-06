# -*- coding: utf-8 -*-
"""Mock web search tool."""

from __future__ import annotations

from datetime import datetime
from typing import Any


def web_search(query: str, top_k: int = 3) -> dict[str, Any]:
    """模拟联网搜索，返回固定但可区分的摘要条目。"""
    top_k = max(1, min(top_k, 5))
    base = [
        {
            "title": f"行业动态：{query[:24]} 相关政策解读",
            "url": "https://news.sparktech.local/policy",
            "snippet": "最新监管要求强调数据出境与人工复核，企业办公自动化需保留审批留痕。",
        },
        {
            "title": f"竞品观察 — {query[:16]} 自动化实践",
            "url": "https://news.sparktech.local/competitor",
            "snippet": "头部 SaaS 已采用多 Agent 编排 + Human-in-the-loop 发送敏感动作。",
        },
        {
            "title": "技术博客：LangGraph interrupt 恢复最佳实践",
            "url": "https://blog.sparktech.local/langgraph",
            "snippet": "使用 checkpointer 持久化 thread state，可在服务重启后 resume 审批。",
        },
    ]
    return {
        "tool": "web_search",
        "query": query,
        "results": base[:top_k],
        "queried_at": datetime.utcnow().isoformat() + "Z",
    }
