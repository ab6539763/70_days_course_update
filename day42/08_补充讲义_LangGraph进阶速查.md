# Day 42 补充讲义 · LangGraph 进阶 API 速查

## Checkpointer

| API | 说明 |
|-----|------|
| `MemorySaver()` | 内存 checkpoint，课堂默认 |
| `SqliteSaver.from_conn_string(path)` | 持久化到 SQLite |
| `configurable.thread_id` | 会话唯一键 |
| `app.get_state(config)` | 读取当前快照 |

## Interrupt

| API | 说明 |
|-----|------|
| `interrupt_before=[...]` | 进入节点前暂停 |
| `interrupt(payload)` | 节点内主动中断并传 payload |
| `Command(resume=x)` | 恢复执行 |

## 并行

| 模式 | 写法 |
|------|------|
| fan-out | 多 edge 从同一源节点出发 |
| 合并 | `Annotated[list, operator.add]` |

## 条件边

```python
graph.add_conditional_edges("node", router_fn, {"a": "node_a", "b": "node_b"})
```

## 常见踩坑

1. 续跑 invoke 覆盖了 checkpoint 字段  
2. 未传 `thread_id` 导致每次新会话  
3. interrupt 后忘记 `Command(resume)` 直接再次 invoke 初始状态  
4. 并行节点写同一标量字段导致覆盖（应用 list + add reducer）
