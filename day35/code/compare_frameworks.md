# LangChain vs LlamaIndex · 星火智服技术选型对照

> Day 35 课堂对照表。LangChain 来自 Day 25–33 实践；LlamaIndex 为今日主线。

## 1. 定位差异

| 维度 | LangChain | LlamaIndex |
|------|-----------|------------|
| 核心口号 | 组装 LLM 应用（Chains / Agents / Tools） | 数据连接与索引（Connect / Index / Query） |
| 强项 | 多步编排、工具调用、Agent 循环 | 文档加载、切块、索引、Query Engine |
| 弱项 | RAG 细节需自己拼组件 | Agent 生态相对 LangGraph 较薄 |
| 学习曲线 | 概念多（Runnable、LCEL） | RAG 路径更「开箱即用」 |
| 星火智服用法 | Day 28–33 知识库原型 | Day 35 重建索引与查询 |

## 2. RAG 组件映射

| 能力 | LangChain（本课程） | LlamaIndex（今日） |
|------|---------------------|-------------------|
| 加载文档 | `DirectoryLoader` + `TextLoader` | `SimpleDirectoryReader` |
| 切块 | `RecursiveCharacterTextSplitter` | `SentenceSplitter` / `NodeParser` |
| 向量存储 | `Chroma` / `FAISS` 集成 | `VectorStoreIndex` 内置 |
| 检索 | `VectorStoreRetriever` | `index.as_retriever()` |
| 问答链 | `RetrievalQA` / LCEL `rag_chain` | `index.as_query_engine()` |
| 评估 | 手写 + Ragas 集成 | 同类，可共用 Day 34 指标 |

## 3. 代码形态对比（伪代码）

### LangChain 风格（Day 33 回顾）

```python
loader = DirectoryLoader("data/", glob="**/*.md")
docs = loader.load()
splits = RecursiveCharacterTextSplitter(chunk_size=256).split_documents(docs)
vectorstore = Chroma.from_documents(splits, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
chain = create_retrieval_chain(retriever, llm)
answer = chain.invoke({"input": question})
```

### LlamaIndex 风格（Day 35）

```python
documents = SimpleDirectoryReader("data/kb_docs").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine(similarity_top_k=3)
response = query_engine.query(question)
```

**讲师结论**：LlamaIndex 用更少样板代码完成「读文档 → 建索引 → 问答」；复杂 Agent 仍倾向 LangChain / LangGraph。

## 4. 何时选谁？

| 场景 | 推荐 | 理由 |
|------|------|------|
| 纯知识库问答 MVP | **LlamaIndex** | 索引与 Query Engine 一等公民 |
| 多工具 Agent + RAG | **LangChain + LangGraph** | 工具环与状态机成熟 |
| 混合检索 + Rerank | 两者皆可 | Day 36 用 LangChain 拼 Rerank；LlamaIndex 有 `QueryFusionRetriever` |
| 团队已投入 LangChain | 继续 LangChain | 迁移成本 > 收益时别换 |
| 文档类型极多（PDF/Notion） | **LlamaIndex** | `SimpleDirectoryReader` 连接器丰富 |

## 5. 星火智服项目决策（虚构评审纪要）

**张工（架构）**：

> Day 33 LangChain 版已跑通；Day 35 用 LlamaIndex **平行实现同一 PRD**，Day 36 答辩对比延迟、代码行数、检索命中率。  
> 生产可双栈：索引服务 LlamaIndex，对外 Agent 仍走 LangChain。

**小陈（产品）**：

> 用户不关心框架，关心 **答案准不准、能不能溯源**。两套实现必须共用 Day 34 评估集。

## 6. 本日验收对照

| 检查项 | LangChain Day 33 | LlamaIndex Day 35 |
|--------|------------------|-------------------|
| 加载 `data/kb_docs/` | ✅ | ✅ `llamaindex_kb.py` |
| Top-K 检索 | k=3 | k=3 |
| mock 无 Key 可跑 | ✅ | ✅ `MockKBEngine` |
| 问答「如何申请退款」 | 命中退款政策 | 同样命中 |
| 评估衔接 | Day 34 `sample_qa_pairs.json` | 共用 |

## 7. 延伸阅读

- LlamaIndex 文档：Data Connectors、Query Engines、Evaluation  
- LangChain 文档：LCEL、Retrieval、LangSmith 追踪  
- Day 36：混合检索 + Cohere Rerank（LangChain 主线）  
- Day 37：企业知识库 MVP 交付

---

**状态**：Day 35 课堂对照讲义 · 随 `llamaindex_kb.py` 联调
