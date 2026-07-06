# 补充讲义 · 高级 RAG 技巧

## 1. 何时用哪种技术

```text
口语/错别字多     → Query Rewrite
召回不足         → Multi-Query 或增大 top_k
问句极短         → HyDE
上下文超长       → Compress / Map-Reduce
精确码/SKU       → BM25 Hybrid（Day 33）
```

## 2. 成本注意

每次额外 LLM 调用增加 latency 与费用；生产环境应对改写结果缓存。

## 3. LangChain 类名对照

| 教学脚本 | LangChain 生态 |
|----------|----------------|
| query_rewrite_demo | `QueryTransformer` |
| multi_query_retriever | `MultiQueryRetriever` |
| hyde_demo | HyDE paper / 社区实现 |
| compress_context | `DocumentCompressorPipeline` |

## 4. 反模式

- 改写改变用户意图（过度发挥）  
- Multi-Query 子句高度重复  
- HyDE 假设文档与知识库风格差异过大
