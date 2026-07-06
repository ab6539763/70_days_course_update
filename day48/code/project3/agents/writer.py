# -*- coding: utf-8 -*-
"""Writer Agent — 起草邮件并准备待审批动作。"""

from __future__ import annotations

from typing import Any

from backend.mock_llm import mock_calendar_event, mock_email_draft
from tools.email_tool import email_draft


class WriterAgent:
    name = "writer"

    def run(self, user_request: str, research_summary: str) -> dict[str, Any]:
        draft_payload = mock_email_draft(user_request, research_summary)
        drafted = email_draft(
            to=draft_payload["to"],
            subject=draft_payload["subject"],
            body=draft_payload["body"],
            cc=draft_payload.get("cc"),
        )
        calendar = mock_calendar_event(user_request)
        needs_meeting = any(k in user_request for k in ("会议", "日程", "预约"))
        return {
            "agent": self.name,
            "summary": "已生成邮件草稿，等待人工审批后发送",
            "details": {
                "email_draft": drafted,
                "calendar_preview": calendar if needs_meeting else None,
            },
            "draft_id": drafted["draft"]["draft_id"],
            "email_preview": draft_payload,
        }
