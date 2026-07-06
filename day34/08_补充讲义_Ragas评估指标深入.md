# Day 34 补充讲义 · Ragas 评估指标深入

## 1. Ragas 指标与今日代码映射

| Ragas 指标 | 本课 `rag_eval_demo` | 典型实现 |
|------------|----------------------|----------|
| faithfulness | `score_faithfulness` | LLM 判断 claim 是否被 context 支持 |
| answer_relevancy | `score_answer_relevance` | 问题↔答案 embedding 相似度 |
| context_precision | `score_context_precision` | 相关 chunk 排序加权 |
| context_recall | `score_context_recall` | GT context 是否被检索覆盖 |

## 2. LLM-as-judge

Ragas 生产模式常调用 LLM：

```text
  Prompt: 给定 context 和 answer，列出 answer 中每个陈述是否可推断
  Output: 0/1 列表 → 平均即 faithfulness
```

优点：理解同义改写、否定句。  
缺点：成本、延迟、本身可能幻觉。

## 3. 测试集建设最佳实践

1. **来源多样**：FAQ、工单、文档章节、人工编写边界 case  
2. **定期刷新**：知识库更新后同步 GT contexts  
3. **分层抽样**：按 category 保证退款/账号/安全均有覆盖  
4. **对抗样本**：故意加入易混淆问法（「取消订单」vs「退款」）

## 4. 指标联动调优

```text
  recall 低 → 加大 Top-K、改切块、混合检索
  precision 低 → Rerank、调 embedding、过滤短 chunk
  faithfulness 低 → 加强「仅根据上下文回答」Prompt、降低 temperature
  relevance 低 → 检索问题或生成 Prompt 问题
```

## 5. 与 LangSmith / Phoenix 的关系

| 工具 | 用途 |
|------|------|
| Ragas | 离线批量评估 |
| LangSmith | 在线 trace + 人工标注 |
| Arize Phoenix | 可视化 embedding 与检索 |

Day 34 脚本是 **最小可复现单元**，日后可接入上述平台。

## 6. 课堂 mock 的局限

- Jaccard 无法理解同义词（「退钱」vs「退款」）  
- 未使用 LLM judge，faithfulness 对 paraphrase 不敏感  
- 生产务必换 **真实 embedding + Ragas live**

---

**状态**：Day 34 补充阅读
