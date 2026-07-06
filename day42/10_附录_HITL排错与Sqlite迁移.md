# Day 42 附录（二）· HITL 排错、Sqlite 迁移与实战剧本

> 本文件为 Day 42 二级附录，配合 `09_附录_Checkpointer与HITL剧本.md` 使用。

---

## 一、interrupt / resume 标准剧本（逐步）

### 剧本 A：CLI 手动两步

```python
from human_in_loop import compile_review_app
from langgraph.types import Command

app = compile_review_app()
config = {"configurable": {"thread_id": "manual-1"}}
initial = {"topic": "退款公告", "draft": "", "human_feedback": "", "approved": False, "revision_count": 0}

p = app.invoke(initial, config)
print("NEXT:", app.get_state(config).next)
print("DRAFT:", p.get("draft", "")[:80])

final = app.invoke(Command(resume="approve"), config)
print("APPROVED:", final.get("approved"))
```

### 剧本 B：修改稿再发

```python
final = app.invoke(Command(resume="【人工修订】退款将于 7 日内原路返回。"), config)
```

预期：`approved=False`，`revision_count>=1`，draft 含修订文。

### 剧本 C：thread 搞错

```python
app.invoke(Command(resume="approve"), {"configurable": {"thread_id": "wrong"}})
```

**台词**：「resume 必须对上首次 invoke 的 thread_id，否则等于新开空会话。」

---

## 二、Checkpointer 故障对照表

| 故障 | 台词 | 一行验证 |
|------|------|----------|
| 状态丢失 | 「未挂 checkpointer」 | `compile(checkpointer=MemorySaver())` |
| resume 无效 | 「thread_id 不一致」 | 打印两边 config |
| count 重置 | 「续跑又传了 count:0」 | 第二次 `invoke({})` |
| 多用户串台 | 「thread_id 应用 user_id」 | compare_threads |
| 文件权限 | 「Sqlite 路径不可写」 | 先 MemorySaver |

---

## 三、SqliteSaver 迁移步骤（选修）

```python
from langgraph.checkpoint.sqlite import SqliteSaver

checkpointer = SqliteSaver.from_conn_string("day42/code/data/checkpoints.db")
app = graph.compile(checkpointer=checkpointer)
```

1. 首次 invoke 写入 db 文件  
2. 退出 Python 进程  
3. 新进程同 thread_id 再 invoke `{}`  
4. 验证 count 续上  

**答辩加分点**：「我们写作助手重启不丢稿。」

---

## 四、writing_agent 调试清单

- [ ] `research_notes` 是否 2 条？  
- [ ] `retry_count` 是否 < MAX 时走 rewrite？  
- [ ] 第三次 `quality_score >= 0.8`？  
- [ ] `status` 为「已发布」或「降级发布」？  
- [ ] 子图 `RESEARCH_SUBGRAPH` 单独 invoke 是否返回 notes？  

---

## 五、面试 6 题

1. **Checkpointer 存什么？** — state snapshot + metadata + next nodes。  
2. **interrupt_before vs interrupt_after？** — 前：节点未跑；后：节点跑完再停。  
3. **Command 还有哪些？** — 如 update state（视版本 API）。  
4. **并行节点失败一路？** — 需错误边或 try/except 节点内降级。  
5. **子图与 Supervisor？** — 子图是模块；Supervisor 是调度多 Agent。  
6. **与 Temporal/Cadence？** — LangGraph 偏 LLM 状态；工作流引擎偏通用任务，可互补。

---

## 六、编码练习

### 练习 1：双 interrupt

在 `publish` 前也加 `interrupt_before=["publish"]`，实现「起草审批 + 发布审批」。

### 练习 2：质检人工

`quality_score < 0.8` 且 `retry_count >= MAX` 时路由到 `human_review` 而非降级发布。

### 练习 3：checkpoint 导出

把 `app.get_state(config)` 序列化到 `data/state_dump.json` 供审计。

---

## 七、5 分钟 Demo 台词

1. 「运营三类问题：丢进度、无审批、太慢——今天五个能力对症。」  
2. `checkpointer_demo`：同一 thread 三次 invoke，count 到 3。  
3. `human_in_loop`：展示 pending_nodes 含 review。  
4. `writing_agent_graph`：并行两路笔记 + 重试环。  
5. 「Day 43 多 Agent Supervisor 接研究报告场景。」

---

## 八、writing_agent 步进跟踪脚本

```python
from writing_agent_graph import compile_writing_app

app = compile_writing_app()
config = {"configurable": {"thread_id": "trace-write"}}
initial = {"topic": "测试", "outline": "", "research_notes": [], "draft": "",
           "quality_score": 0.0, "retry_count": 0, "status": "init"}

for event in app.stream(initial, config):
    print(event)
```

观察何时出现 `write`、`quality` 重复（重试环）。

---

## 九、合规场景：公告发布双闸

1. `interrupt_before=["review"]` — 内容合规  
2. `interrupt_before=["publish"]` — 发布权限  

两次 resume 可对应运营主管 + 法务，thread_id 相同。

---

## 十、面试追问：Checkpointer 存哪

- MemorySaver：进程堆  
- SqliteSaver：本地文件  
- PostgresSaver：共享 DB，多副本 Worker 续跑同一 thread  

星火生产选型 Postgres + Redis 锁（选修阅读）。

---

*Day 42 二级附录完*
