# Project 3 · 多 Agent 智能办公助手

LangGraph 编排的办公自动化 Demo：**Planner → Researcher → Writer → 人工审批 → Executor**。

## 能力清单

| 类别 | 内容 |
|------|------|
| Agent | planner, researcher, writer, executor |
| 工具 | calendar×2, email×2, web_search, document_rag, task_list×2 |
| 编排 | LangGraph + MemorySaver checkpointer |
| 人工门控 | `interrupt()` 审批后发邮件/建日程 |
| API | FastAPI `/api/tasks` 创建 / 查询 / resume |

## 快速开始

```bash
cd day48/code/project3
pip install -r requirements.txt
export PYTHONPATH=$PWD SPARKTECH_MOCK=1
python3 verify_project3.py
bash run.sh
```

浏览器打开 `http://127.0.0.1:8088`，提交任务后在审批面板点「批准发送」。

## 目录

```
project3/
├── agents/          # 多 Agent 节点逻辑
├── tools/           # 日历/邮件/搜索/RAG/任务列表
├── graph/           # office_graph.py + checkpointer
├── backend/         # FastAPI
├── frontend/        # 简易审批 UI
├── data/sample_docs/
├── verify_project3.py
└── run.sh
```

**代码主线在 day48**；Day 49–50 课件引用同一路径。
