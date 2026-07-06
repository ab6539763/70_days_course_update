# -*- coding: utf-8 -*-
"""
Day 46 · 可观测性演示（LangSmith 概念 · mock 模式）

不依赖真实 LangSmith API，用内存 Span 树模拟：
- Run / Span 层级
- 延迟与 token 估算
- 失败标记与导出 JSON

运行：cd day46/code && python3 observability_demo.py
"""

from __future__ import annotations

import json
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Generator, Iterator


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Span:
    name: str
    span_type: str = "chain"
    run_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    parent_id: str | None = None
    start_time: str = field(default_factory=_utc_now)
    end_time: str | None = None
    latency_ms: float = 0.0
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    children: list["Span"] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def finish(self, outputs: dict[str, Any] | None = None, *, error: str | None = None) -> None:
        self.end_time = _utc_now()
        if outputs:
            self.outputs = outputs
        self.error = error

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "type": self.span_type,
            "run_id": self.run_id,
            "parent_id": self.parent_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "latency_ms": self.latency_ms,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "error": self.error,
            "metadata": self.metadata,
            "children": [c.to_dict() for c in self.children],
        }


class MockTracer:
    """模拟 LangSmith Tracer：记录 Run 树。"""

    def __init__(self, project: str = "sparktech-day46") -> None:
        self.project = project
        self._stack: list[Span] = []
        self.root_runs: list[Span] = []

    @contextmanager
    def trace(self, name: str, *, span_type: str = "chain", **inputs: Any) -> Generator[Span, None, None]:
        parent = self._stack[-1] if self._stack else None
        span = Span(name=name, span_type=span_type, parent_id=parent.run_id if parent else None, inputs=dict(inputs))
        if parent:
            parent.children.append(span)
        else:
            self.root_runs.append(span)
        self._stack.append(span)
        t0 = time.perf_counter()
        try:
            yield span
        except Exception as exc:  # noqa: BLE001
            span.finish(error=str(exc))
            raise
        finally:
            span.latency_ms = round((time.perf_counter() - t0) * 1000, 2)
            if span.end_time is None:
                span.finish()
            self._stack.pop()

    def export_json(self) -> str:
        return json.dumps(
            {"project": self.project, "runs": [r.to_dict() for r in self.root_runs]},
            ensure_ascii=False,
            indent=2,
        )


def estimate_tokens(text: str) -> int:
    """教学用粗估：中文按字、英文按词。"""
    return max(1, len(text) // 2)


class ObservableAgentDemo:
    """演示 Agent 各步骤如何被 trace。"""

    def __init__(self, tracer: MockTracer | None = None) -> None:
        self.tracer = tracer or MockTracer()

    def run(self, user_query: str) -> dict[str, Any]:
        with self.tracer.trace("agent_run", span_type="agent", query=user_query) as root:
            with self.tracer.trace("llm_plan", span_type="llm", messages_count=2) as llm_span:
                time.sleep(0.02)
                plan = "call_tool:lookup_order"
                llm_span.metadata["tokens_in"] = estimate_tokens(user_query)
                llm_span.metadata["tokens_out"] = 12
                llm_span.finish({"plan": plan})

            with self.tracer.trace("tool_lookup_order", span_type="tool", order_id="ST-10086") as tool_span:
                time.sleep(0.01)
                tool_span.finish({"status": "shipped"})

            with self.tracer.trace("llm_summarize", span_type="llm") as sum_span:
                time.sleep(0.015)
                answer = "订单 ST-10086 已发货，预计 2026-07-08 送达。"
                sum_span.metadata["tokens_out"] = estimate_tokens(answer)
                sum_span.finish({"answer": answer})

            root.finish({"answer": answer})
            return {"answer": answer, "trace_id": root.run_id}


def demo_failure_trace() -> Span:
    tracer = MockTracer(project="sparktech-failure-demo")
    with tracer.trace("agent_run", query="死循环测试") as root:
        with tracer.trace("llm_round_1", span_type="llm") as s1:
            s1.finish({"tool_calls": ["search", "search"]})
        with tracer.trace("llm_round_2", span_type="llm") as s2:
            s2.finish({"tool_calls": ["search"]})
        with tracer.trace("guard_max_rounds", span_type="guard") as g:
            g.finish({}, error="max_rounds_exceeded")
        root.finish({"answer": "[blocked] 超过最大轮次"})
    return root


def print_trace_tree(span: Span, indent: int = 0) -> None:
    prefix = "  " * indent
    err = f" ERROR={span.error}" if span.error else ""
    print(f"{prefix}├─ {span.name} ({span.latency_ms}ms){err}")
    for child in span.children:
        print_trace_tree(child, indent + 1)


def main() -> None:
    demo = ObservableAgentDemo()
    result = demo.run("查订单 ST-10086")
    print("=== Agent 回答 ===")
    print(result["answer"])
    print("\n=== Trace 树（类 LangSmith UI）===")
    for root in demo.tracer.root_runs:
        print_trace_tree(root)
    print("\n=== JSON 导出片段 ===")
    print(demo.tracer.export_json()[:500], "...")

    print("\n=== 失败 trace 示例 ===")
    fail_tracer = MockTracer()
    demo_failure_trace()
    for root in fail_tracer.root_runs:
        print_trace_tree(root)


if __name__ == "__main__":
    main()
