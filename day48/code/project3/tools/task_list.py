# -*- coding: utf-8 -*-
"""Structured task list tool — 衔接 Day 4 CRUD 思路。"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

_TASKS: list[dict[str, Any]] = []


def task_list_add(title: str, priority: Literal["low", "medium", "high"] = "medium") -> dict[str, Any]:
    task_id = f"task-{len(_TASKS) + 1:03d}"
    item = {
        "id": task_id,
        "title": title,
        "priority": priority,
        "status": "open",
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    _TASKS.append(item)
    return {"tool": "task_list_add", "task": item}


def task_list_list(status: str | None = None) -> dict[str, Any]:
    items = _TASKS if status is None else [t for t in _TASKS if t["status"] == status]
    return {"tool": "task_list_list", "tasks": list(items)}


def reset_task_store() -> None:
    global _TASKS
    _TASKS = []
