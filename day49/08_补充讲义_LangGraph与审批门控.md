# Day 49 补充讲义 · LangGraph 与审批门控

## 1. interrupt 三要素

1. **节点内**调用 `interrupt(payload)`  
2. **checkpointer** 持久化 thread state  
3. **resume** 使用 `Command(resume=user_input)`  

## 2. 何时设 interrupt

| 动作 | 建议 |
|------|------|
| 外发邮件 | 必须 |
| 创建对外日历 | 必须 |
| 内部 RAG 查询 | 否 |
| 草稿生成 | 否 |

## 3. API 错误码

| 码 | 场景 |
|----|------|
| 404 | thread 不存在 |
| 409 | 已完成仍 resume |

## 4. 调试命令

```bash
curl -X POST localhost:8010/api/tasks -H 'Content-Type: application/json' \
  -d '{"request":"测试邮件"}'
curl localhost:8010/api/tasks/<thread_id>
curl -X POST localhost:8010/api/tasks/<thread_id>/resume \
  -H 'Content-Type: application/json' \
  -d '{"approval":{"decision":"approve"}}'
```

## 5. 答辩高频题

- interrupt 与 while 循环人工确认的区别？—— 框架级 checkpoint，可跨请求恢复  
- MemorySaver 局限？—— 进程重启丢状态；生产用 Sqlite/Postgres  
- 多 Agent 与单 Agent ReAct？—— 本项固定 DAG，职责清晰，便于教学审计  

---

*Day 49 补充讲义*
