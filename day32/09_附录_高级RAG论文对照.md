# Day 32 附录 · 高级 RAG 论文与实现对照

---

## 一、Query Rewriting

**论文思想**：用户问法口语化，检索 query 应书面化。  
**实现**：`query_rewrite_demo.py` 用 LLM 或规则改写。  
**业务例**：「咋退款啊」→「退款政策与申请流程」

---

## 二、Multi-Query

生成 N 个子问题分别检索，合并去重。  
**收益**：提高 recall；**成本**：N 倍检索。

---

## 三、HyDE（Hypothetical Document Embeddings）

1. 让 LLM 写「假设性答案文档」  
2. 对假设文档做 embedding 检索  
3. 用检索到的真实 chunk 生成最终答案  

**适用**：问句与文档表述差异大。

---

## 四、Context Compression

检索 top_k 过大时，用 LLM 或启发式删掉无关句。  
见 `hyde_demo.py` 中 `compress_context`。

---

## 五、与 Day 33 衔接

| Day 32 | Day 33 |
|--------|--------|
| 改 query | 改检索器 |
| 多路 query | BM25+向量 |
| HyDE | RRF+Rerank |

---

## 六、现场辩论题

「HyDE 会不会引入幻觉文档？」——讨论：只用于检索向量，不直接给用户。

---

*附录完。*
