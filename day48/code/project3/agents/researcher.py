# -*- coding: utf-8 -*-
"""Researcher Agent — 调用 RAG 与联网搜索收集依据。"""

from __future__ import annotations

from typing import Any

from backend.mock_llm import mock_research_summary
from tools.document_rag import document_rag_search
from tools.web_search import web_search


class ResearcherAgent:
    name = "researcher"

    def run(self, user_request: str, plan: list[str]) -> dict[str, Any]:
        rag = document_rag_search(user_request, top_k=3)
        web = web_search(user_request, top_k=2)
        summary = mock_research_summary(user_request, rag.get("hits", []), web.get("results", []))
        return {
            "agent": self.name,
            "summary": summary,
            "details": {
                "plan_ref": plan,
                "rag": rag,
                "web": web,
            },
        }
