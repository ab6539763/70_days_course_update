# -*- coding: utf-8 -*-
"""
Day 43 · Agent 角色定义

研究团队三角色：Searcher / Analyst / Writer
+ Supervisor 路由元数据
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from langchain_core.messages import AIMessage, HumanMessage

from mock_llm import build_chat_model


@dataclass
class AgentResult:
    agent: str
    content: str
    artifacts: dict = field(default_factory=dict)


@dataclass
class AgentRole:
    name: str
    description: str
    system_prompt: str
    mock_response: str

    def run(self, task: str, context: str = "") -> AgentResult:
        llm = build_chat_model(responses=[self.mock_response])
        prompt = (
            f"{self.system_prompt}\n\n"
            f"任务: {task}\n"
            f"上下文:\n{context or '(无)'}"
        )
        reply = str(llm.invoke([HumanMessage(content=prompt)]).content)
        return AgentResult(agent=self.name, content=reply, artifacts={"task": task})


SEARCHER = AgentRole(
    name="searcher",
    description="检索公开资料、文档与案例",
    system_prompt="你是 Searcher：只输出检索到的要点列表，附来源标签。",
    mock_response=(
        "[searcher] 检索结果:\n"
        "1. LangGraph Supervisor 官方示例 (docs.langchain.com)\n"
        "2. 多 Agent 编排模式对比 (blog)\n"
        "3. SparkTech 内部 KB: Agent 审批流案例"
    ),
)

ANALYST = AgentRole(
    name="analyst",
    description="归纳检索结果，提炼洞察与风险",
    system_prompt="你是 Analyst：基于检索笔记写结构化分析，含 pros/cons。",
    mock_response=(
        "[analyst] 分析摘要:\n"
        "- Supervisor 适合动态路由\n"
        "- 风险: 子 Agent 输出格式不一致\n"
        "- 建议: 统一 JSON schema 交付物"
    ),
)

WRITER = AgentRole(
    name="writer",
    description="将分析转为对业务方可读的报告",
    system_prompt="你是 Writer：输出 Markdown 报告，含标题、摘要、建议。",
    mock_response=(
        "# 研究报告\n\n"
        "## 摘要\n"
        "Supervisor 模式可编排 Searcher→Analyst→Writer 流水线。\n\n"
        "## 建议\n"
        "1. 定义 handoff schema\n"
        "2. 为每个子 Agent 设超时与重试"
    ),
)

RESEARCH_TEAM: dict[str, AgentRole] = {
    "searcher": SEARCHER,
    "analyst": ANALYST,
    "writer": WRITER,
}

SUPERVISOR_PROMPT = """你是研究团队 Supervisor。
根据当前任务阶段，选择下一步执行的 agent：
- searcher: 需要外部检索
- analyst: 已有检索结果，需要分析
- writer: 已有分析，需要成稿
- FINISH: 报告已完成

只返回 agent 名称（searcher/analyst/writer/FINISH），不要解释。"""


def pick_next_agent_mock(stage: str, has_search: bool, has_analysis: bool, has_report: bool) -> str:
    """mock 路由：按流水线顺序推进。"""
    if not has_search:
        return "searcher"
    if not has_analysis:
        return "analyst"
    if not has_report:
        return "writer"
    return "FINISH"


def format_handoff(results: list[AgentResult]) -> str:
    lines = []
    for r in results:
        lines.append(f"### {r.agent}\n{r.content}\n")
    return "\n".join(lines)


def run_agent(name: str, task: str, context: str = "") -> AgentResult:
    role = RESEARCH_TEAM.get(name)
    if not role:
        raise ValueError(f"未知 agent: {name}")
    return role.run(task, context)


AgentRunner = Callable[[str, str, str], AgentResult]
