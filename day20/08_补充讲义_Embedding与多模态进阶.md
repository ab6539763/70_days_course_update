# Day 20 补充讲义 · Embedding 与多模态进阶

---

## 1. 常见相似度度量

| 度量 | 公式特点 | 适用 |
|------|----------|------|
| 余弦 similarity | 方向，忽略长度 | 文本 embedding 主流 |
| 欧氏距离 | 绝对距离 | 未归一化向量 |
| 点积 | 受长度影响 | 归一化后等同 cosine |
| 曼哈顿 | L1 距离 | 稀疏向量 |

**实践**：OpenAI embedding 已归一化，cosine = 点积。

## 2. Embedding 模型选型

| 模型 | 维度 | 特点 |
|------|------|------|
| text-embedding-3-small | 可调 | 性价比高 |
| text-embedding-3-large | 可调 | 质量更高 |
| 开源 bge/m3e | 固定 | 可本地部署 |

选型维度：语种（中文）、维度、延迟、成本、是否可私有化。

## 3. 检索优化路径

```text
Brute-force cosine（本日）
    → FAISS / HNSW ANN（Day 21）
    → 混合检索 BM25 + 向量
    → Cross-encoder 重排序
```

## 4. 多模态进阶

### 4.1 图片限制

- 分辨率与 token 消耗  
- 支持格式：PNG、JPEG、GIF、WebP  
- 多图：content 数组多张 image_url  

### 4.2 安全

- 用户上传需病毒扫描、大小限制  
- 图片可能含敏感信息，日志脱敏  

## 5. FAQ 去重

对标准问两两算 cosine，> 0.95 可视为重复，合并条目减少索引噪音。

## 6. 与 RAG 的关系

```text
用户问 → embed query → 检索 chunks → 拼 prompt → LLM 生成
```

本日 `similar_question_matcher` 是 RAG 的 **检索子模块** 特例（chunk = 整条 FAQ）。

## 7. 调试清单

- [ ] 向量是否 L2 归一化  
- [ ] 索引与查询是否同一 embedding 模型  
- [ ] threshold 是否按类目分化  
- [ ] 变体测试集是否覆盖口语  
- [ ] live/mock 混用导致维度不一致  

---

**延伸阅读**：MTEB 中文榜单、ColBERT 晚期交互检索。
