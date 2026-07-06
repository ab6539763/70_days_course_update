# 阶段四学习路径索引 · Day 39–50（Agent 智能体）

> 从 RAG 问答升级到 **自主规划 + 工具调用 + 多 Agent 协作**。

---

## 一、阶段目标

交付 **星火智服 Phase3**：多 Agent 智能办公助手（项目三），具备日程/邮件/搜索/RAG、人工审批、任务中断恢复。

---

## 二、每日导航

| 天 | 目录 | 关键词 | 验收 |
|----|------|--------|------|
| 39 | day39/ | ReAct 手写 | `verify_day39.py` |
| 40 | day40/ | LangChain Agent | `verify_day40.py` |
| 41 | day41/ | LangGraph 图 | `verify_day41.py` |
| 42 | day42/ | HITL / Checkpointer | `verify_day42.py` |
| 43 | day43/ | Supervisor | `verify_day43.py` |
| 44 | day44/ | MCP | `verify_day44.py` |
| 45 | day45/ | 周测 + Dify | `verify_day45.py` |
| 46 | day46/ | 护栏 / Trace | `verify_day46.py` |
| 47 | day47/ | Text-to-SQL | `verify_day47.py` |
| 48–50 | day48/code/project3/ | **项目三** | `verify_project3.py` |

---

## 二点五、扩展附录（09/10）

阶段四薄弱日已补齐 **扩展主课**（与 Day 25–38 体例一致）：

| 天 | 附录 | 主题 |
|----|------|------|
| 39 | 09 | ReAct 论文对照与手写循环精读 |
| 40 | 09/10 | LangChain Agent 手把手 + 排错面试 |
| 41 | 09/10 | LangGraph 状态图精读 + 图调试 |
| 42 | 09/10 | Checkpointer/HITL 剧本 + Sqlite 迁移 |
| 43 | 09/10 | Supervisor 设计模式 + 20 题自测 |
| 44 | 09/10 | MCP 协议速查 + 安全面试 |
| 45 | 09 | 第五周周测与 Dify 对照 |
| 46 | 09/10 | 可观测性护栏 + LangSmith 对照 |
| 47 | 09/10 | Text2SQL 安全 + 恶意 SQL 实验 |
| 48 | 09 | Project3 架构深度导读 |
| 49 | 09/10 | 全栈联调手把手 + API 契约 |
| 50 | 09/10 | 答辩评委 30 题 + 三项目对比表 |

**阅读顺序**：`04_课堂讲义.md` → `08_补充讲义` → `09/10_附录`。

---

## 三、技术演进链

```mermaid
flowchart LR
    D19[Day19 Function Calling] --> D39[Day39 ReAct]
    D39 --> D40[LC Agent]
    D40 --> D41[LangGraph]
    D41 --> D42[HITL]
    D42 --> D43[Multi-Agent]
    D43 --> D48[Project3]
    D36[Day36 RAG] --> D48
```

---

## 四、项目三启动

```bash
cd day48/code/project3
pip install -r requirements.txt
export SPARKTECH_MOCK=1 PYTHONPATH=$PWD
python3 verify_project3.py
bash run.sh
# http://127.0.0.1:8088
```

**端口**：API `8010`，前端 `8088`（与 project2 的 8000/8080 区分）

---

## 五、与前三阶段项目对照

| 项目 | 天数 | 核心能力 |
|------|------|----------|
| 一 | 14 | 命令行多轮对话 |
| 二 | 36–38 | RAG + 引用 + Web |
| 三 | 48–50 | 多 Agent + 审批 + 工具链 |

---

*索引 · 2026-07-06*
