# Day 29 补充讲义 · Chroma 与检索进阶

## 1. Chroma vs 其他向量库

| 库 | 场景 |
|----|------|
| Chroma | 本地 PoC、课程 |
| Milvus / Qdrant | 生产大规模 |
| pgvector | 已有 PostgreSQL |

## 2. 集合与维度

- 同一 `collection` 内向量 **维度必须一致**  
- 换 embedding 模型需 **重建索引**  

## 3. 检索优化

- **MMR**：多样性，避免 Top-K 重复  
- **Hybrid**：BM25 + 向量（Day 30+ 选做）  
- **Reranker**：cross-encoder 精排  

## 4. 生产注意

- 定期 `build_vectorstore` 增量更新  
- 备份 `chroma_db/` 目录  
- 监控检索延迟 P99  

---

*延伸：LangChain Chroma 集成文档*
