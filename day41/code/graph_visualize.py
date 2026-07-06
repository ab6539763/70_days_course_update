# -*- coding: utf-8 -*-
"""
Day 41 · LangGraph 图结构可视化

导出 Mermaid / ASCII 图，便于课堂讲解 Node、Edge、Conditional Edge。

运行：cd day41/code && python3 graph_visualize.py
"""

from __future__ import annotations

from pathlib import Path

from langgraph_react import build_react_graph


def export_mermaid(output: Path | None = None) -> str:
    """从编译前 graph 生成 Mermaid（手写模板 + 节点列表）。"""
    g = build_react_graph()
    # LangGraph 编译前可用 nodes 属性
    nodes = list(g.nodes.keys()) if hasattr(g, "nodes") else ["reason", "act"]

    mermaid = """```mermaid
flowchart TD
    __start__([START]) --> reason[reason 推理节点]
    reason -->|有 Action| act[act 工具节点]
    reason -->|Final Answer / 超时| __end__([END])
    act --> reason
```"""
    if output:
        output.write_text(mermaid.replace("```mermaid\n", "").replace("```", ""), encoding="utf-8")
    return mermaid


def export_ascii() -> str:
    """ASCII 版图示。"""
    return """
┌─────────┐
│  START  │
└────┬────┘
     ▼
┌─────────┐     Final Answer / max_steps
│ reason  │──────────────────────────────┐
│ (Node)  │                              │
└────┬────┘                              ▼
     │ Action                      ┌─────────┐
     ▼                             │   END   │
┌─────────┐                        └─────────┘
│   act   │
│ (Node)  │
└────┬────┘
     │ Edge (固定)
     └──────────▶ reason
"""


def demo_conditional_edges() -> None:
    """讲解条件边。"""
    print("=" * 60)
    print("条件边 should_continue 逻辑")
    print("=" * 60)
    print("""
def should_continue(state) -> Literal["act", "end"]:
    if state["done"]:           return "end"
    if state["step"] >= 6:      return "end"
    if has Final Answer:        return "end"
    if has Action:              return "act"
    return "end"
""")


def main() -> None:
    out_dir = Path(__file__).resolve().parent / "output"
    out_dir.mkdir(exist_ok=True)

    print("=" * 60)
    print("Day 41 · graph_visualize.py")
    print("=" * 60)

    mermaid = export_mermaid(out_dir / "react_graph.mmd")
    print("\n[Mermaid]")
    print(mermaid)

    print("\n[ASCII]")
    print(export_ascii())

    demo_conditional_edges()

    # 尝试 langgraph 自带 draw_mermaid（若可用）
    try:
        from langgraph_react import compile_react_agent

        app = compile_react_agent()
        if hasattr(app, "get_graph"):
            g = app.get_graph()
            if hasattr(g, "draw_mermaid"):
                print("\n[LangGraph 自动生成 Mermaid]")
                print(g.draw_mermaid())
    except Exception as exc:  # noqa: BLE001
        print(f"\n[提示] get_graph.draw_mermaid 跳过: {exc}")

    print(f"\n已写入: {out_dir / 'react_graph.mmd'}")
    print("\n✅ graph_visualize.py 完成")


if __name__ == "__main__":
    main()
