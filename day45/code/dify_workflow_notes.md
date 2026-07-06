# Dify / Coze 低代码工作流学习笔记 · Day 45

> **说明**：本文档为课堂共创笔记模板。无 API Key 亦可完成阅读与对比表填写；有账号同学可补充截图链接。

---

## 一、为什么在第 5 周讲低代码？

星火智服 Phase3 启动会上，产品问：

> 「你们手写 Agent 两周了，运营同事能不能自己改 Prompt、接知识库、发 Bot？」

张工的回答要点：

1. **PoC 与运营迭代**：Dify / Coze 适合快速搭演示、让非开发同学校验流程。  
2. **工程边界**：权限、审计、复杂工具、与 ERP 深度集成——往往仍需 Python 自研。  
3. **人才视角**：懂低代码边界，才能正确选型，而不是「全外包给平台」或「全盘否定平台」。

---

## 二、Dify 工作流核心概念

| 概念 | 含义 | 代码类比 |
|------|------|----------|
| App | 一个可发布的应用 | `integrated_agent_review.py` 进程 |
| Workflow | 可视化 DAG | LangGraph `StateGraph` |
| Node | 单步处理（LLM、知识检索、HTTP） | LCEL Runnable / tool |
| Edge | 节点连线与条件 | 条件边 `add_conditional_edges` |
| Knowledge | 知识库数据集 | Day 36 Chroma + ingest |
| Tool | 外部 API / 插件 | `ToolRegistry` |

### 2.1 典型客服工作流（ASCII）

```text
[用户输入] → [意图分类 LLM] → 条件分支
                ├─ FAQ → [知识库检索] → [回答 LLM] → [输出]
                ├─ 工单 → [HTTP 创建工单] → [确认话术]
                └─ 闲聊 → [直接 LLM]
```

### 2.2 与 Day 45 代码对照

`integrated_agent_review.py` 中的工具环：

```text
user → mock_llm → tool_calls? → ToolRegistry.execute → tool 消息 → mock_llm → final_answer
```

Dify 工作流把「菱形判断」画在画布上；代码里用 `for round_idx in range(MAX_ROUNDS)` 实现。

---

## 三、Dify vs Coze vs 自研代码

| 维度 | Dify | Coze（扣子） | 自研 Python Agent |
|------|------|--------------|-------------------|
| 可视化编排 | ✅ 强 | ✅ 强 | 需 LangGraph Studio 等 |
| 私有部署 | ✅ 开源可自建 | 以云服务为主 | ✅ 完全自控 |
| 国内模型接入 | 需配置 | 较便捷 | 自行封装 Client |
| 复杂工具链 | 插件生态 | 插件 / Bot | 任意 Python |
| CI/CD 与单测 | 较弱 | 较弱 | pytest + verify 脚本 |
| 适合阶段 | PoC、运营迭代 | 快速 Bot、抖音生态 | 生产核心链路 |

**课堂填空**（作业 32 题）：在「私有部署」行补充你的结论。

---

## 四、何时选低代码、何时坚持代码？

### 4.1 适合 Dify / Coze

- 一周内要给业务方可点的 Demo  
- 运营频繁改 Prompt、换知识库文档  
- 工具仅为标准 HTTP API，无复杂事务  

### 4.2 坚持自研（本课程主线）

- 与现有 FastAPI / ERP / 审批流深度耦合（Day 48+）  
- 需要 `verify_dayNN.py` 级自动化回归  
- 数据不出内网、细粒度 RBAC  

### 4.3 混合策略（企业常见）

```text
Dify 做外部 FAQ Bot → 复杂工单转发自研 Agent API
```

---

## 五、迁移清单：项目二知识库 → Dify

若将 Day 36–38 知识库问答迁入 Dify，建议：

| 组件 | 迁移到 Dify | 建议保留自研 |
|------|-------------|--------------|
| 文档摄取清洗 | 可用 Dify Knowledge | 复杂 PDF 流水线 |
| 混合检索 + Rerank | 部分支持 | 精细调参实验台 |
| 引用溯源格式 | 可配置 | 与客户合同一致的 JSON |
| 用户权限 / 审计 | 平台 RBAC | 与企业 SSO 对接层 |

**预习 Day 46**：无论 Dify 还是自研，生产都要加 **guardrails、tracing、重试**。

---

## 六、动手建议（无账号也可做）

1. 阅读 [Dify 文档](https://docs.dify.ai/) Workflow 章节目录。  
2. 浏览 Coze 官方「工作流」介绍页，记录 3 个节点类型名称。  
3. 在 `integrated_agent_review.py` 运行 `/tools`，画一张与之等价的 Dify 草图。  

---

*笔记版本：Day 45 · SparkTech 培训 · 可提交 PR 补充截图*
