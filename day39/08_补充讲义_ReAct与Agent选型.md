# Day 39 补充讲义 · ReAct 与 Agent 架构选型

## 1. 主流 Agent 范式

| 范式 | 特点 | 适用场景 |
|------|------|----------|
| **ReAct** | 逐步 Thought→Action | 工具少、需可解释 |
| **Function Calling** | API 结构化 tool_calls | 生产稳定、OpenAI 生态 |
| **Plan-and-Execute** | 先规划后执行 | 步骤多、可并行 |
| **Reflexion** | 失败后自我反思 | 高容错任务 |

今日手写 ReAct；Day 19 已练 FC；Day 40 用 LangChain FC Agent。

## 2. ReAct 优缺点

**优点**

- Thought 链可审计，客服主管能看懂  
- 不绑定特定 API 格式，通义/文心也能用  
- 教学友好，循环逻辑清晰  

**缺点**

- 文本解析脆弱（多余 markdown、幻觉 Action 名）  
- 每步都调 LLM，延迟与成本高  
- 难以 parallel tools（对比 Day 19 并行 tool_calls）  

## 3. 星火智服 Phase3 选型建议

```text
工单路由 Agent
├── 意图分类：规则 + 小模型（今日 mock 规则）
├── 知识检索：Day 36 Hybrid RAG
├── 路由决策：ReAct / LangGraph（Day 41 加审批）
└── 高风险操作：人工 approval 节点（Day 41）
```

## 4. Prompt 工程要点

1. **严格格式**：system prompt 明确 Action Input 必须 JSON  
2. **工具清单**：名称与 `TOOL_REGISTRY` 完全一致  
3. **Observation 勿编造**：强调「工具结果由系统填入」  
4. **Few-shot**：可在 prompt 放 1 个完整 ReAct 范例  

## 5. 与 MCP 的关系

MCP（Model Context Protocol）标准化工具发现与调用；本质仍是 Agent 循环 + 工具 schema。  
Day 19 JSON schema ≈ MCP tool definition 简化版。

## 6. 调试清单

- [ ] 打印每步 raw LLM 输出  
- [ ] Observation 是否合法 JSON  
- [ ] Action 名是否在 TOOL_REGISTRY  
- [ ] max_steps 是否合理  
- [ ] mock LLM 是否覆盖你的 demo 话术  

---

*Day 39 补充讲义*
