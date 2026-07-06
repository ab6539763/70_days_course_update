# -*- coding: utf-8 -*-
"""Day 68 · 架构组件清单生成。"""

from __future__ import annotations

COMPONENTS = [
    "API Gateway", "Auth", "Rate Limiter", "LLM Router",
    "Vector DB", "Object Storage", "Cache", "Queue",
    "Observability", "Guardrails",
]


def checklist(selected: list[str]) -> dict:
    missing = [c for c in ("API Gateway", "Auth", "Observability") if c not in selected]
    return {"selected": selected, "missing_critical": missing, "ready": len(missing) == 0}


if __name__ == "__main__":
    print(checklist(COMPONENTS[:5]))
