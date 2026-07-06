# Day 48 补充讲义 · Agent 与工具开发速查

## 1. 工具设计 Checklist

- [ ] 函数名动词开头：`search`, `draft`, `schedule`  
- [ ] 返回 dict 含 `tool` 字段  
- [ ] 写操作与读操作分文件或分函数  
- [ ] 提供 `reset_*_store()` 供单测  
- [ ] 不 import LLM / Agent  

## 2. Agent 设计 Checklist

- [ ] `name` 类属性固定  
- [ ] `run()` 返回 `agent`, `summary`, `details`  
- [ ] 不直接操作全局 UI  
- [ ] mock 与 live 分支集中在 `mock_llm` 或 client 层  

## 3. LangGraph 预习（Day 49）

```python
from langgraph.types import interrupt, Command

def human_gate(state):
    decision = interrupt({"preview": state["pending_approval"]})
    ...

graph.invoke(Command(resume={"decision": "approve"}), config)
```

## 4. 常见答辩题（预习）

1. 为何需要 checkpointer？—— 服务重启后恢复 interrupt 状态  
2. Planner 与 Researcher 能否合并？—— 教学拆分职责；生产可合并降延迟  
3. mock RAG 与 Project 2 Hybrid 差异？—— 本项轻量关键词；KB 项目用 BM25+向量  

## 5. 推荐阅读

- LangGraph interrupt 文档  
- Day 18 结构化输出与安全（人工门控预告）  
- Day 35 框架对比（LangChain vs LlamaIndex）  

---

*Day 48 补充讲义*
