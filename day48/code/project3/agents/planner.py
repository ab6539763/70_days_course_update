# -*- coding: utf-8 -*-
"""Planner Agent — 拆解用户办公请求为可执行计划。"""

from __future__ import annotations

from typing import Any

from backend.mock_llm import mock_plan


class PlannerAgent:
    name = "planner"

    def run(self, user_request: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        plan = mock_plan(user_request)
        return {
            "agent": self.name,
            "plan": plan,
            "summary": f"已拆解为 {len(plan)} 步执行计划",
            "details": {"steps": plan, "context": context or {}},
        }
