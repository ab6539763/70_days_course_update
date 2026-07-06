# Day 41 补充讲义 · LangGraph 进阶

## 1. Checkpointer

| 实现 | 场景 |
|------|------|
| MemorySaver | 课堂 demo |
| SqliteSaver | 单机持久化 |
| PostgresSaver | 生产多实例 |

配合 `thread_id` 实现多工单并行编排。

## 2. Human-in-the-Loop

```python
graph.compile(interrupt_before=["approval"])
```

UI 展示 State → 人工修改 `approved` → 继续 invoke。

## 3. 与 Day 36 RAG 组合

```text
reason → act(search_kb) → reason → act(classify) → approval? → route
```

检索结果写入 State `kb_snippets` 字段供 reason 节点使用。

## 4. 调试

- `app.get_state(config)` 查看当前 State  
- LangSmith 追踪每 Node 耗时  
- `stream_mode="updates"` 逐节点输出  

## 5. 何时用 LangGraph vs AgentExecutor

| 场景 | 推荐 |
|------|------|
| 简单 tool 循环 | AgentExecutor |
| 多分支审批 | LangGraph |
| 长时间运行 / 暂停 | LangGraph + Checkpointer |
| 多 Agent 协作 | LangGraph 多节点 |

---

*Day 41 补充*
