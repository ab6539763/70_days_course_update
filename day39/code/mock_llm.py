# -*- coding: utf-8 -*-
"""
Day 39 · Mock LLM for ReAct（无 API Key 教学用）

启发式生成 ReAct 格式文本：Thought / Action / Action Input / Final Answer
"""

from __future__ import annotations

import json
import os
import re
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None  # type: ignore

try:
    import requests
except ImportError:
    requests = None  # type: ignore


REACT_SYSTEM_TEMPLATE = """你是星火智服 Phase3 工单路由助手。使用 ReAct 格式逐步推理并调用工具。

可用工具：
{tools}

输出格式（严格遵守）：
Thought: <你的推理>
Action: <工具名>
Action Input: <JSON 或简短文本>

收到 Observation 后继续 Thought，直到可以回答用户则输出：
Thought: <总结>
Final Answer: <给用户的最终答复>

规则：
- 每次只调用一个 Action
- Action Input 必须是合法 JSON 或工具要求的简短参数
- 不要编造 Observation，工具结果会由系统填入
"""


@dataclass
class LLMResponse:
    text: str
    mode: str
    latency_ms: float = 0.0
    raw: dict[str, Any] = field(default_factory=dict)


def is_mock_mode() -> bool:
    flag = os.getenv("SPARKTECH_MOCK", "").lower()
    if flag in ("1", "true", "yes"):
        return True
    return not os.getenv("OPENAI_API_KEY", "").strip()


class ReActLLMClient:
    """ReAct 专用 LLM：live 调 API，mock 用启发式 ReAct 文本。"""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        if load_dotenv:
            load_dotenv()
        self._api_key = (api_key or os.getenv("OPENAI_API_KEY") or "").strip()
        self._base_url = (base_url or os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
        self._model = model or os.getenv("OPENAI_MODEL") or "gpt-4o-mini"
        self._timeout = timeout
        self._step = 0

    @property
    def mode(self) -> str:
        return "mock" if is_mock_mode() else "live"

    def complete(self, messages: list[dict[str, str]]) -> LLMResponse:
        start = time.perf_counter()
        if is_mock_mode():
            text = self._mock_complete(messages)
            mode = "mock"
        else:
            text = self._live_complete(messages)
            mode = "live"
        latency = (time.perf_counter() - start) * 1000
        return LLMResponse(text=text, mode=mode, latency_ms=round(latency, 2))

    def reset(self) -> None:
        self._step = 0

    def _live_complete(self, messages: list[dict[str, str]]) -> str:
        if requests is None:
            raise RuntimeError("未安装 requests")
        url = f"{self._base_url}/chat/completions"
        payload = {
            "model": self._model,
            "messages": messages,
            "temperature": 0.2,
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=self._timeout)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"] or ""

    def _mock_complete(self, messages: list[dict[str, str]]) -> str:
        """按对话阶段返回预设 ReAct 步骤。"""
        user_text = ""
        last_obs: dict[str, Any] | None = None
        for msg in reversed(messages):
            if msg.get("role") == "user" and not user_text:
                user_text = msg.get("content", "")
            if msg.get("role") == "assistant" and "Observation:" in msg.get("content", ""):
                obs_match = re.search(r"Observation:\s*(.+)", msg["content"], re.DOTALL)
                if obs_match:
                    try:
                        last_obs = json.loads(obs_match.group(1).strip())
                    except json.JSONDecodeError:
                        pass
                break

        self._step += 1
        text = user_text.lower()

        # 若上一条含 Observation，决定下一步或 Final Answer
        if last_obs is not None:
            if "intent" in last_obs and self._step <= 3:
                intent = last_obs["intent"]
                tier = "vip" if "vip" in text or "加急" in user_text else "standard"
                return (
                    f"Thought: 已分类为 {intent}，需要路由到对应技能组。\n"
                    f"Action: route_ticket\n"
                    f'Action Input: {{"intent": "{intent}", "customer_tier": "{tier}"}}'
                )
            if "team" in last_obs:
                team = last_obs.get("team_label", last_obs.get("team"))
                sla = last_obs.get("sla_hours", "?")
                return (
                    f"Thought: 路由完成，可以汇总给用户。\n"
                    f"Final Answer: 工单已自动路由至【{team}】，预计 SLA {sla} 小时内响应。"
                    f"（mock 模式，完整链路：分类→路由）"
                )
            if "snippets" in last_obs:
                titles = [s["title"] for s in last_obs.get("snippets", [])[:2]]
                return (
                    f"Thought: 已检索到知识库依据。\n"
                    f"Final Answer: 参考知识库：{'、'.join(titles) or '无匹配'}。"
                    f"建议按政策处理。（mock）"
                )

        # 第一步：分类或检索
        if any(k in user_text for k in ("退款", "退费", "账单")):
            return (
                "Thought: 用户描述涉及退款，应先 classify_ticket 确定意图。\n"
                "Action: classify_ticket\n"
                f'Action Input: {{"text": "{user_text[:80]}"}}'
            )
        if any(k in user_text for k in ("api", "500", "报错", "接口")):
            return (
                "Thought: 技术故障类，先查知识库再分类。\n"
                "Action: search_kb_snippet\n"
                f'Action Input: {{"query": "API 500 错误", "limit": 2}}'
            )
        if "tk-" in text or "工单" in user_text:
            tid_match = re.search(r"TK-\d{8}-\d{3}", user_text, re.I)
            tid = tid_match.group(0) if tid_match else "TK-20260702-002"
            return (
                f"Thought: 用户提供了工单号，先查询详情。\n"
                f"Action: get_ticket_by_id\n"
                f'Action Input: {{"ticket_id": "{tid}"}}'
            )
        if re.search(r"\d+\s*[\*\+\-\/]\s*\d+", user_text):
            expr_match = re.search(r"(\d[\d\s+\-*/().]*)", user_text)
            expr = expr_match.group(1).strip() if expr_match else "2+2"
            return (
                "Thought: 需要计算优先级或表达式。\n"
                "Action: calculate\n"
                f'Action Input: {{"expression": "{expr}"}}'
            )

        return (
            "Thought: 一般咨询，先分类。\n"
            "Action: classify_ticket\n"
            f'Action Input: {{"text": "{user_text[:80] or "一般咨询"}"}}'
        )


def build_system_prompt(tools_block: str) -> str:
    return REACT_SYSTEM_TEMPLATE.format(tools=tools_block)
