# -*- coding: utf-8 -*-
"""Day 66 · 简历项目描述生成器。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ProjectBullet:
    name: str
    stack: str
    impact: str

    def to_bullet(self) -> str:
        return f"【{self.name}】{self.stack} — {self.impact}"


PROJECTS = [
    ProjectBullet("星火智服 RAG", "FastAPI+Chroma+混合检索", "企业知识库问答，citations 溯源"),
    ProjectBullet("多 Agent 办公", "LangGraph+HITL", "审批门控+8工具链"),
    ProjectBullet("LoRA 客服模型", "LLaMA-Factory+vLLM+Docker", "降本35%目标架构"),
]


def build_resume_section() -> str:
    return "\n".join(p.to_bullet() for p in PROJECTS)


if __name__ == "__main__":
    print(build_resume_section())
