# 补充讲义 · Hybrid 检索与重排

## 1. 融合策略对比

| 方法 | 优点 | 缺点 |
|------|------|------|
| 分数加权 | 直观 | 需校准量纲 |
| RRF | 稳健、无校准 | 丢失绝对分数 |
| 级联 | 省算力 | 一路 miss 则全 miss |

## 2. Rerank 成本

对 N 个候选做 cross-encoder，复杂度 O(N)。通常 N≤20。

## 3. Parent Document 参数

- child 180–300 字符  
- parent = 业务自然段（章节/页面）  

## 4. LangChain 对照

| 今日代码 | LangChain |
|----------|-----------|
| HybridRetriever | `EnsembleRetriever` + BM25 |
| reciprocal_rank_fusion | `RRFRanker` |
| Parent index | `ParentDocumentRetriever` |

## 5. 生产清单

```text
□ Hybrid 双路索引同步更新
□ Rerank 超时降级（跳过重排）
□ Parent 映射一致性
□ 监控各阶段 latency
```
