# Day 30 补充讲义 · RAG 评测与防幻觉

## 1. 幻觉类型

| 类型 | 对策 |
|------|------|
| 无检索瞎编 | 强制仅据上下文 + 拒答 |
| 检索噪声 | 提高 threshold、Rerank |
| 引用错误 | citations 从 metadata 自动生成 |

## 2. 评测指标

- **Faithfulness**：答案是否可由上下文推出  
- **Answer Relevance**：是否答非所问  
- **Context Precision**：检索块是否相关  

## 3. 生产增强

- HyDE、Multi-Query 扩展检索  
- 流式输出 + 引用高亮  
- 审计日志：query、chunks、prompt hash  

## 4. 安全

- Prompt 注入：上下文与用户问题分隔  
- 敏感信息：入库前脱敏  

---

*Day 30 KEY DAY 补充 · 张工*
