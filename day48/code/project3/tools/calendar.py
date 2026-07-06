# -*- coding: utf-8 -*-
"""Mock calendar tools — list and schedule events."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

_EVENTS: list[dict[str, Any]] = [
    {
        "id": "evt-001",
        "title": "周会 Standup",
        "start": "2026-07-07T09:30:00+08:00",
        "end": "2026-07-07T10:00:00+08:00",
        "location": "线上",
    }
]


def calendar_list(days: int = 7) -> dict[str, Any]:
    """列出未来若干天内的日历事件（mock）。"""
    days = max(1, min(days, 30))
    return {
        "tool": "calendar_list",
        "days": days,
        "events": list(_EVENTS),
        "queried_at": datetime.utcnow().isoformat() + "Z",
    }


def calendar_schedule(
    title: str,
    start: str,
    end: str,
    attendees: list[str] | None = None,
    location: str = "3F 会议室 A",
) -> dict[str, Any]:
    """创建日历事件（mock，立即写入内存 store）。"""
    event_id = f"evt-{len(_EVENTS) + 1:03d}"
    record = {
        "id": event_id,
        "title": title,
        "start": start,
        "end": end,
        "attendees": attendees or [],
        "location": location,
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    _EVENTS.append(record)
    return {"tool": "calendar_schedule", "status": "scheduled", "event": record}


def reset_calendar_store() -> None:
    """测试用：重置日历数据。"""
    global _EVENTS
    _EVENTS = [
        {
            "id": "evt-001",
            "title": "周会 Standup",
            "start": "2026-07-07T09:30:00+08:00",
            "end": "2026-07-07T10:00:00+08:00",
            "location": "线上",
        }
    ]
