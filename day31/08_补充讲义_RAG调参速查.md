# 补充讲义 · RAG 调参速查表

## 1. 参数速查

| 参数 | 常见范围 | 增大时倾向 | 减小時倾向 |
|------|----------|------------|------------|
| chunk_size | 256–1024 | 块更完整、粒度粗 | 更精细、更碎 |
| chunk_overlap | 50–150 | 边界语义保留好 | 索引体积变小 |
| top_k | 3–10 | 召回↑ 噪声↑ | 上下文短 |
| embedding dim | 512–1536 | 表达力↑ 成本↑ | 速度快 |

## 2. 诊断清单

```text
□ 评测集是否固定？
□ 是否只看 top-1 忽略 top-k 分布？
□ 生成幻觉 → 先查检索是否相关
□ 精确码查不到 → 考虑 BM25 hybrid（Day 33）
□ 口语问法查不到 → 考虑 query rewrite（Day 32）
```

## 3. LangChain 常用 import

```python
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma  # 持久化选做
```

## 4. mock vs live

| 模式 | 用途 |
|------|------|
| mock | 流程、CI、课堂无 Key |
| live | 真实排序、上线前验证 |

切换：`SPARKTECH_MOCK=0` 且配置 `OPENAI_API_KEY`。

## 5. 延伸阅读

- LangChain Text Splitters 文档  
- MTEB embedding 排行榜（选模型参考）  
- Day 32 HyDE / Multi-Query  
- Day 33 RRF + Reranker
