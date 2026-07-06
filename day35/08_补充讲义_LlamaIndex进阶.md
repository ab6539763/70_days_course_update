# Day 35 补充讲义 · LlamaIndex 进阶

## 1. 核心模块速查

| 模块 | 说明 |
|------|------|
| `llama_index.core` | Document、Index、QueryEngine |
| `llama_index.core.node_parser` | SentenceSplitter、SemanticSplitter |
| `llama_index.core.readers` | SimpleDirectoryReader |
| `llama_index.vector_stores` | Chroma、Qdrant、Milvus 等 |
| `llama_index.embeddings` | OpenAI、HuggingFace |

## 2. Node vs Document

```text
  Document（整篇 PDF/MD）
       │
       ▼ SentenceSplitter
  Node（带 metadata 的 chunk）
       │
       ▼
  Index 只索引 Node
```

metadata 常用：`file_name`、`page_label`、`category`。

## 3. 进阶 Query 模式

### 3.1 子问题查询（Sub Question Query Engine）

复杂问题拆成多个子问，分别检索再汇总。

### 3.2 路由查询（Router Query Engine）

按问题类型选择不同 Index（如「政策」vs「技术文档」）。

### 3.3 CitationQueryEngine

答案中自动插入 `[1][2]` 引用标记。

## 4. 与 LangChain 互操作

LlamaIndex 可将 Index 导出为 LangChain `VectorStoreRetriever`：

```python
# 概念示例（版本 API 可能变化）
retriever = index.as_retriever()
# 接入 LangChain LCEL chain
```

适合 **索引用 LlamaIndex、Agent 用 LangChain** 的混合架构。

## 5. 性能提示

| 场景 | 建议 |
|------|------|
| 文档 < 1 万 chunk | 默认 `VectorStoreIndex` 内存即可 |
| 文档 > 10 万 | 外置 Qdrant / Milvus |
| 频繁更新 | 增量 `insert` Node，避免全量重建 |
| 中文长文档 | `chunk_overlap=32~64`，避免句中断 |

## 6. 今日 MockKBEngine 与真实 Index 差异

| 项 | Mock | LlamaIndex |
|----|------|------------|
| 相似度 | Jaccard + 二元组 | Embedding cosine |
| 切块 | `##` 标题 | SentenceSplitter |
| 生成 | 模板取首句 | LLM 综合多 chunk |

评估请统一用 Day 34 黄金集，勿用 mock 分数做生产决策。

---

**状态**：Day 35 补充阅读
