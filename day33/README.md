# Day 33 · Hybrid 检索 · RRF 融合 · Rerank · Parent Document 增强 RAG

> **旁白（讲师口吻）**  
> 周三评审，李姐指着监控：*「SKU 和错误码用向量老 miss，口语用 BM25 也 miss——**Day 33 上 Hybrid + RRF，再加 reranker 和 parent document**。」*  
> 张工：*「`enhanced_rag_pipeline.py` 要把 Day 31–32 串成可演示的一条链。」*

---

## 今日学习地图

| 时段 | 主题 | 产出物 |
|------|------|--------|
| 09:00–10:30 | BM25 + 向量 + RRF | `hybrid_retriever.py` |
| 10:30–12:00 | bge-reranker / mock rerank | `rerank_demo.py` |
| 14:00–16:00 | Parent Document Retriever | `enhanced_rag_pipeline.py` |
| 16:00–17:00 | 端到端演示 + verify | 全绿截图 |
| 19:00–21:00 | 作业 | `06_课后作业.md` |

## 今日文件清单

| 文件 | 用途 |
|------|------|
| [01_业务背景.md](./01_业务背景.md) | Hybrid 检索业务驱动 |
| [02_需求文档.md](./02_需求文档.md) | 增强 RAG PRD |
| [03_架构与设计.md](./03_架构与设计.md) | 全链路架构 |
| [04_课堂讲义.md](./04_课堂讲义.md) | **主课** |
| [05_流程图与示意图.md](./05_流程图与示意图.md) | RRF / Parent 流程 |
| [06_课后作业.md](./06_课后作业.md) | 作业 |
| [07_作业参考答案.md](./07_作业参考答案.md) | 参考答案 |
| [08_补充讲义_Hybrid与重排.md](./08_补充讲义_Hybrid与重排.md) | 速查 |
| [code/hybrid_retriever.py](./code/hybrid_retriever.py) | BM25+Vector+RRF |
| [code/rerank_demo.py](./code/rerank_demo.py) | 重排序 |
| [code/enhanced_rag_pipeline.py](./code/enhanced_rag_pipeline.py) | **全链路** |
| [code/verify_day33.py](./code/verify_day33.py) | 验收 |
| [run.sh](./run.sh) | 一键演示 |

## 验收标准

- [ ] 能解释 RRF 公式与 BM25/向量互补性  
- [ ] Hybrid 检索 + Rerank + Parent 管道可运行  
- [ ] `verify_day33.py` 全部 `[OK]`  
- [ ] Git commit 含 `day33`

## 快速开始

```bash
cd day33
bash run.sh
cd code && python3 verify_day33.py
```

**状态**：✅ Day 33 Hybrid 增强 RAG 完整课件已发布
