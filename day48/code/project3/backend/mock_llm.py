# -*- coding: utf-8 -*-
"""Deterministic mock LLM for offline demos and verify script."""

from __future__ import annotations

import json
import re
from typing import Any


def mock_plan(user_request: str) -> list[str]:
    text = user_request.lower()
    steps: list[str] = []
    if any(k in text for k in ("会议", "日程", "预约", "calendar", "meeting")):
        steps.append("检索内部制度与竞品动态")
        steps.append("拟定会议议程与参会人")
        steps.append("创建日历事件并起草通知邮件")
    elif any(k in text for k in ("邮件", "email", "通知", "回复")):
        steps.append("检索相关知识库段落")
        steps.append("联网补充最新政策或新闻")
        steps.append("起草邮件并等待人工审批后发送")
    else:
        steps.append("分析用户意图并拆解子任务")
        steps.append("调用检索工具收集依据")
        steps.append("生成可执行交付物（邮件/日程）")
    return steps


def mock_research_summary(user_request: str, rag_hits: list[dict], web_hits: list[dict]) -> str:
    rag_part = rag_hits[0]["snippet"][:80] if rag_hits else "未命中内部文档"
    web_part = web_hits[0]["title"] if web_hits else "未命中外部资讯"
    return (
        f"针对「{user_request[:40]}」：内部依据——{rag_part}；"
        f"外部参考——{web_part}。"
    )


def mock_email_draft(user_request: str, research: str) -> dict[str, Any]:
    subject = "【星火智服】办公协同通知"
    if "退款" in user_request:
        subject = "退款政策说明与后续安排"
    elif "会议" in user_request or "meeting" in user_request.lower():
        subject = "会议邀请：产品评审与行动项同步"

    body = (
        f"各位同事好，\n\n"
        f"根据您的需求：{user_request.strip()}\n\n"
        f"调研摘要：{research}\n\n"
        f"请查收并回复确认。此邮件由多 Agent 办公助手起草，发送前需人工审批。\n\n"
        f"—— 星火智服 Office Copilot"
    )
    return {
        "to": ["team@sparktech.local"],
        "cc": [],
        "subject": subject,
        "body": body,
    }


def mock_calendar_event(user_request: str) -> dict[str, Any]:
    return {
        "title": "产品协同会议" if "会议" in user_request else "办公协同事项",
        "start": "2026-07-08T10:00:00+08:00",
        "end": "2026-07-08T11:00:00+08:00",
        "attendees": ["zhang@sparktech.local", "chen@sparktech.local"],
        "location": "3F 会议室 A",
    }


def try_parse_json(text: str) -> dict[str, Any] | None:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return None
