# Day 29 附录 · Chroma 运维与检索速查

---

## 一、持久化目录

```python
Chroma(persist_directory="./chroma_db", embedding_function=emb)
```

**注意**：重建索引前备份或 `--rebuild` 清库。

---

## 二、similarity_search 参数

| 参数 | 含义 |
|------|------|
| k | 返回条数 |
| filter | metadata 过滤 `{"source": "faq"}` |
| score_threshold | 距离阈值（版本 API 差异） |

---

## 三、Mock Embedding 原理（教学）

`MockEmbeddings` 用哈希向量保证：

- 同文本同向量  
- 相似词有一定重叠（n-gram）  

**无 API Key 可跑通全链路**，但不可用于生产评估。

---

## 四、Retriever 接口

```python
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
docs = retriever.invoke("如何退款")
```

Day 30 `rag_pipeline` 直接消费 `List[Document]`。

---

## 五、实验记录

| 查询 | top1 source | score | 是否相关 |
|------|-------------|-------|----------|
| 退款 | faq_refund.txt | | |
| 工单 | product_guide.md | | |

---

## 六、故障排查

| 现象 | 处理 |
|------|------|
| 空检索 | 是否 ingest |
| 维度过错 | embedding 模型不一致 |
| 锁文件 | 单进程写 chroma |

---

*附录完。*
