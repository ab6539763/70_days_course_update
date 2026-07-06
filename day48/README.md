# Day 48 · STAGE PROJECT 3（上）· 多 Agent 办公助手 — 架构与工具

> **旁白（讲师口吻）**  
> 周一晨会，运营总监摊开需求单：*「不是单轮 Chat 了——要 **会查制度、会搜新闻、会起草邮件、会约会议**，发出去前还得 **人工点确认**。」*  
> 张工在白板画出四个 Agent 与 LangGraph 状态机：**Project 3 三天交付**——今天定架构、写工具、跑通 Agent 节点。

---

## 今日学习地图

| 时段 | 主题 | 产出物 |
|------|------|--------|
| 09:00–10:00 | 需求评审 & 多 Agent 架构 | `02_需求文档.md` `03_架构与设计.md` |
| 10:00–12:00 | 工具层开发（日历/邮件/搜索/RAG） | `tools/*.py` |
| 14:00–15:30 | Agent 角色划分与节点实现 | `agents/*.py` |
| 15:30–17:00 | 单测与 `verify_project3` 工具段 | 全绿截图 |
| 17:00–17:30 | 里程碑签收 | README 签收栏 |
| 19:00–21:00 | 作业：扩展工具或样本文档 | `06_课后作业.md` |

## 里程碑定位

```mermaid
flowchart LR
    D39[Day39 Agent基础] --> D48[Day48 架构+工具]
    D48 --> D49[Day49 LangGraph+API]
    D49 --> D50[Day50 答辩]
    D50 --> M[Project3 结业]
```

**Day 48 是 Project 3 第一天**：完成架构、≥3 Agent 节点、≥5 工具、mock 可运行；LangGraph 全链路与前端在 Day 49 联调。

## 项目代码位置

```
day48/code/project3/
├── agents/          # planner, researcher, writer
├── tools/           # calendar, email, search, rag, task_list
├── graph/           # office_graph.py（Day49 深化）
├── backend/         # FastAPI（Day49 完善）
├── frontend/        # 审批 UI（Day49 联调）
├── verify_project3.py
└── run.sh
```

## 今日文件清单

| 文件 | 用途 |
|------|------|
| [01_业务背景.md](./01_业务背景.md) | 办公自动化立项 |
| [02_需求文档.md](./02_需求文档.md) | Project 3 PRD |
| [03_架构与设计.md](./03_架构与设计.md) | 多 Agent + 工具注册表 |
| [04_课堂讲义.md](./04_课堂讲义.md) | **主课** 工具与 Agent |
| [05_流程图与示意图.md](./05_流程图与示意图.md) | 协作时序图 |
| [06_课后作业.md](./06_课后作业.md) | 扩展作业 |
| [07_作业参考答案.md](./07_作业参考答案.md) | 参考答案 |
| [08_补充讲义_Agent与工具开发.md](./08_补充讲义_Agent与工具开发.md) | 工具契约速查 |
| [code/project3/](./code/project3/) | **项目代码** |
| [verify_project3.py](./verify_project3.py) | 验收入口 |

## 今日验收标准

- [ ] 能解释 Planner / Researcher / Writer 职责边界  
- [ ] 工具 ≥5：`calendar` `email` `web_search` `document_rag` `task_list`  
- [ ] `document_rag_search` 能命中 `data/sample_docs/`  
- [ ] 三个 Agent 节点可独立 `run()` 并产出结构化 dict  
- [ ] mock 模式无 API Key 可演示  
- [ ] `python3 verify_project3.py` 工具与 Agent 段 `[OK]`  
- [ ] Git commit message 含 `day48`

## 快速开始

```bash
cd day48/code/project3
pip install -r requirements.txt
export PYTHONPATH=$PWD SPARKTECH_MOCK=1
python3 verify_project3.py
```

---

**讲师提醒**：今日不要求前端与 interrupt 联调完整——那是 Day 49 主线；但 `graph/office_graph.py` 骨架已预埋。

**状态**：✅ Day 48 Project 3（上）完整课件已发布
