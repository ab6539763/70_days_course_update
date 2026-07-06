# Day 32 · 高级 RAG · 查询改写 · Multi-Query · HyDE · 上下文压缩

> **旁白（讲师口吻）**  
> 周一晨会，客服反馈：*「用户问『能退钱吗』，知识库写的是『退款政策』——向量检索经常漏。」*  
> 李姐：*「Day 32 上 **查询改写、多查询、HyDE**；下午把检索前处理链跑通，mock 也要能演示增益。」*

---

## 今日学习地图

| 时段 | 主题 | 产出物 |
|------|------|--------|
| 09:00–10:30 | 查询改写原理与 Prompt | `query_rewrite_demo.py` |
| 10:30–12:00 | Multi-Query 合并去重 | `multi_query_retriever.py` |
| 14:00–15:30 | HyDE 假设文档检索 | `hyde_demo.py` |
| 15:30–16:30 | 上下文压缩策略 | `hyde_demo.compress_context` |
| 16:30–17:00 | `verify_day32.py` 验收 | 全绿截图 |
| 19:00–21:00 | 作业 | `06_课后作业.md` |

## 今日文件清单

| 文件 | 用途 |
|------|------|
| [01_业务背景.md](./01_业务背景.md) | 口语问法与文档措辞鸿沟 |
| [02_需求文档.md](./02_需求文档.md) | 高级 RAG PRD |
| [03_架构与设计.md](./03_架构与设计.md) | 检索前处理链架构 |
| [04_课堂讲义.md](./04_课堂讲义.md) | **主课** |
| [05_流程图与示意图.md](./05_流程图与示意图.md) | Multi-Query / HyDE 流程 |
| [06_课后作业.md](./06_课后作业.md) | 必做 / 选做 |
| [07_作业参考答案.md](./07_作业参考答案.md) | 参考答案 |
| [08_补充讲义_高级RAG技巧.md](./08_补充讲义_高级RAG技巧.md) | 技巧速查 |
| [code/query_rewrite_demo.py](./code/query_rewrite_demo.py) | 查询改写 |
| [code/multi_query_retriever.py](./code/multi_query_retriever.py) | 多查询检索 |
| [code/hyde_demo.py](./code/hyde_demo.py) | HyDE + 压缩 |
| [code/verify_day32.py](./code/verify_day32.py) | 验收 |
| [run.sh](./run.sh) | 一键演示 |

## 验收标准

- [ ] 能口述 Query Rewrite / Multi-Query / HyDE 适用场景  
- [ ] 三个 demo 脚本 mock 模式可运行  
- [ ] `verify_day32.py` 全部 `[OK]`  
- [ ] Git commit 含 `day32`

## 快速开始

```bash
cd day32
bash run.sh
cd code && python3 verify_day32.py
```

**状态**：✅ Day 32 高级 RAG 完整课件已发布
