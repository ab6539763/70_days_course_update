# -*- coding: utf-8 -*-
"""Mock email draft / send tools."""

from __future__ import annotations

from datetime import datetime
from typing import Any

_DRAFTS: list[dict[str, Any]] = []
_SENT: list[dict[str, Any]] = []


def email_draft(to: list[str], subject: str, body: str, cc: list[str] | None = None) -> dict[str, Any]:
    """生成邮件草稿（不发送）。"""
    draft_id = f"draft-{len(_DRAFTS) + 1:03d}"
    record = {
        "draft_id": draft_id,
        "to": to,
        "cc": cc or [],
        "subject": subject,
        "body": body,
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    _DRAFTS.append(record)
    return {"tool": "email_draft", "status": "drafted", "draft": record}


def email_send(draft_id: str) -> dict[str, Any]:
    """发送已审批的邮件（mock）。"""
    draft = next((d for d in _DRAFTS if d["draft_id"] == draft_id), None)
    if not draft:
        return {"tool": "email_send", "status": "error", "message": f"draft {draft_id} not found"}
    sent = {
        **draft,
        "sent_at": datetime.utcnow().isoformat() + "Z",
        "message_id": f"msg-{len(_SENT) + 1:05d}",
    }
    _SENT.append(sent)
    return {"tool": "email_send", "status": "sent", "message": sent}


def reset_email_store() -> None:
    global _DRAFTS, _SENT
    _DRAFTS = []
    _SENT = []
