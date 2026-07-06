# Day 40 补充讲义 · LangChain Agent 进阶

## 1. Agent 类型选型

| API | 适用 |
|-----|------|
| `create_tool_calling_agent` | OpenAI/通义等支持 tool_calls 的模型 |
| `create_react_agent` | 文本 ReAct 模板（老模型） |
| `create_structured_chat_agent` | 结构化输出约束 |

今日用 tool_calling，与 Day 19 最接近。

## 2. 常见坑

- **忘记 MessagesPlaceholder**：scratchpad 无法注入  
- **tool 返回非 str**：建议 JSON.dumps  
- **max_iterations 过小**：多步路由被截断  
- **handle_parsing_errors**：建议 True  

## 3. 与 Day 36 RAG 集成

生产 `search_kb` 应：

```python
# 调用 project2 检索 API 或 import HybridRetriever
```

## 4. 可观测性

`return_intermediate_steps=True` 可对接 LangSmith trace。

---

*Day 40 补充*
