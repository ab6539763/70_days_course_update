# Day 43 补充讲义 · Supervisor 模式选型

## 何时用 Supervisor

- 子任务 **顺序不固定** 或需 **反复检查**  
- 需要 **中心审计日志**（谁做了什么）  
- 子 Agent **异构**（不同 prompt / 工具 / 模型）

## 何时不用

- 固定 ETL → 用 Pipeline  
- 低延迟简单问答 → 单 Agent + RAG  
- 大量对等讨论 → Swarm / Group Chat

## 生产 checklist

| 项 | 说明 |
|----|------|
| 超时 | 每个子 Agent 独立 timeout |
| 格式 | handoff JSON schema |
| 幂等 | 同 task_id 可重放 |
| 成本 | Supervisor 用小模型 |
| 观测 | steps / messages 写日志 |

## LangGraph 实现要点

- worker → supervisor 回边形成 **环**  
- `conditional_edges` 映射 agent 名到节点名  
- `MemorySaver` 支持长研究任务断点续跑（与 Day 42 结合）
