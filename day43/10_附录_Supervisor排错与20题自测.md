# Day 43 附录（二）· Supervisor 排错、20 题自测与项目三对照

> 本文件为 Day 43 二级附录，配合 `09_附录_Supervisor设计模式.md` 使用。

---

## 一、Supervisor 死循环与步数防护

### 现象

messages 里 supervisor 重复 `route -> searcher`，steps>50。

### 根因

- `search_result` 未写入（worker 异常）  
- `pick_next_agent` 永不返回 FINISH  
- writer 未设置 `report` 字段  

### 修复模板

```python
def supervisor_node(state: TeamState) -> dict:
    if state.get("steps", 0) >= 20:
        return {"current_agent": "FINISH", "messages": [...], "steps": state["steps"] + 1}
    ...
```

---

## 二、20 题自测（含答案）

1. **Supervisor 与 Pipeline 最大区别？** — 动态路由 vs 固定顺序。  
2. **子 Agent 能否再调工具？** — 可以，封装在 worker 节点内。  
3. **黑板 state 存什么？** — 各阶段产物 + 调度元数据。  
4. **handoff 作用？** — 把上游产物格式化给下游。  
5. **为何 worker 回 supervisor？** — 支持返工与动态加步。  
6. **FINISH 如何表达？** — current_agent 字符串 + route 映射 end。  
7. **mock 路由局限？** — 无法模拟「分析不足重做搜索」。  
8. **如何加 Reviewer？** — 新节点 + 扩展 pick + 边表。  
9. **steps 字段用途？** — 限流、计费、可观测。  
10. **与 CrewAI 对比？** — 同为角色分工；本课用 LangGraph 显式图。  
11. **Searcher 输出太长？** — 截断或摘要再 handoff。  
12. **多任务并行？** — 多 thread_id，每任务一图实例。  
13. **Supervisor 用同一 LLM？** — 可与 worker 分模型降本。  
14. **format_handoff 可换 JSON 吗？** — 推荐生产用 schema。  
15. **finalize 兜底顺序？** — report → analysis → search。  
16. **Checkpointer 必须？** — 长任务推荐，短 demo 可选。  
17. **Swarm 何时选？** — 无明确阶段，需辩论式协作。  
18. **项目三为何固定图？** — 办公 SOP 稳定，少运行时路由风险。  
19. **如何测 Searcher？** — 单测 `run_agent('searcher',...)`。  
20. **MCP 接哪？** — Searcher.run 内调 MCP Client。

---

## 三、代码阅读闯关

### 关卡 1

`supervisor_multi_agent.py` 中 `add_edge(worker, "supervisor")` 有几条？  
→ 3 条（searcher/analyst/writer）。

### 关卡 2

第一次进入 supervisor 时 `has_search` 为何 False？  
→ 初始 state 空字符串，bool("")=False。

### 关卡 3

writer 完成后 `current_agent` 是 writer 还是 FINISH？  
→ supervisor 下一轮才设 FINISH；writer 节点设 current_agent=writer。

---

## 四、业务剧本

| 用户任务 | 预期 agents 顺序 |
|----------|------------------|
| 行业简报 | searcher→analyst→writer |
| 仅查资料 | 可扩展 FINISH 在 analyst 前（需改 pick） |
| 报告差评返工 | supervisor 再派 writer（live LLM 路由） |

---

## 五、面试快答

- **Supervisor 会不会成为瓶颈？** — 调度轻量；重活在 worker。  
- **如何保证一致性？** — schema + 校验节点。  
- **多 Supervisor 层级？** — 层级模式，上级管下级小组。

---

## 六、5 分钟 Demo 台词

1. 「市场部周报：检索、分析、成稿三角色。」  
2. `supervisor_multi_agent.py` 打印 messages 时间线。  
3. 打开 `agent_roles.py` 三份 system_prompt。  
4. 强调 worker 回 supervisor 的环，非直线 pipeline。  
5. 「明日 MCP 标准化 Searcher 后端。」

---

## 七、Handoff JSON Schema 草案（生产）

```json
{
  "version": "1",
  "from_agent": "analyst",
  "artifacts": {
    "insights": ["string"],
    "risks": ["string"]
  }
}
```

Writer system_prompt 增加：「仅使用 artifacts 内字段。」

---

## 八、Supervisor Prompt 注入示例

```python
def build_supervisor_messages(state: TeamState) -> str:
    return f"""任务: {state['task']}
已有检索: {bool(state.get('search_result'))}
已有分析: {bool(state.get('analysis_result'))}
已有报告: {bool(state.get('report'))}
请返回 searcher|analyst|writer|FINISH"""
```

替换 `pick_next_agent_mock` 即得 live 版（需注意解析稳定性）。

---

## 九、课堂辩论题

**辩题**：行业简报是否应固定 Pipeline 而非 Supervisor？  
**正方**：成本可预测、易测  
**反方**：分析不足时可返工 searcher  
**裁判要点**：返工频率数据决定选型  

---

## 十、研究报告 Demo 台词扩展版（8 min）

1. 背景：「单 Agent 写行业简报，检索和分析质量不稳定。」  
2. 架构图：「Supervisor 只调度，Searcher/Analyst/Writer 分工。」  
3. 运行 `supervisor_multi_agent.py`，指 messages 四步。  
4. 打开 report Markdown 预览。  
5. 对比：「若固定 Pipeline，返工 searcher 要改图；Supervisor 只需多一轮路由。」  
6. 预告 MCP：「Searcher 后端明日标准化。」  
7. 预告项目三：「办公助手用固定图，但思想相同。」  
8. Q&A 准备：死循环、成本、schema。  

---

## 十一、与 Day 42 writing_agent 对比

| | writing_agent | supervisor team |
|--|---------------|-----------------|
| 角色 | 单图多节点 | 多 Agent 角色 |
| 并行 | plan→search∥analyze | 串行阶段（可扩展并行 searcher） |
| 调度 | 固定边 | supervisor 条件边 |

可辩论：行业简报是否应用 writing_agent 的并行调研 + supervisor 成稿。

---

*Day 43 二级附录完*
