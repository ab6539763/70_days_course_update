# Day 19 补充讲义 · Function Calling 进阶

> 面向已掌握主课的学员：并行工具、错误恢复、与 MCP 对比。

---

## 1. parallel tool_calls

OpenAI 模型可在一次响应中返回多个 tool_call：

```json
"tool_calls": [
  {"id": "call_1", "function": {"name": "get_weather", ...}},
  {"id": "call_2", "function": {"name": "calculate", ...}}
]
```

执行策略：

| 工具类型 | 建议 |
|----------|------|
| HTTP / DB 查询 | 可并行 |
| 有状态写操作 | 串行或加锁 |
| calculate | 串行即可 |

```python
import asyncio

async def run_tool_calls_async(calls):
    return await asyncio.gather(*(asyncio.to_thread(run_tool_call, c) for c in calls))
```

## 2. 工具错误与模型重试

当 `tool` 消息含错误时，模型可能：
1. 修正参数重试  
2. 换工具  
3. 向用户解释失败  

**最佳实践**：错误 content 用结构化 JSON，保留 `tool_call_id`。

## 3. tool_choice 参数

| 值 | 行为 |
|----|------|
| `"auto"` | 模型决定（默认） |
| `"none"` | 禁止工具 |
| `{"type":"function","function":{"name":"get_weather"}}` | 强制调用指定工具 |

强制工具适用于流水线场景（如必须先鉴权再查询）。

## 4. 与 ReAct / MCP 对比

| 方案 | 特点 |
|------|------|
| OpenAI Function Calling | 结构化 JSON，工业标准 |
| ReAct 文本 | Thought/Action 可解释，解析脆弱 |
| MCP (Model Context Protocol) | 标准化工具宿主，跨客户端 |

张工观点：

> 「先掌握 OpenAI FC 格式；MCP 是把它包装成可插拔服务。」

## 5. 安全清单

- [ ] 工具函数白名单，禁止 `eval` 用户输入  
- [ ] DB 查询参数化，防注入  
- [ ] 工具返回勿含密钥、PII  
- [ ] 限制 `max_rounds` 与单次 tool 超时  
- [ ] 记录 audit log：谁调了什么工具  

## 6. 调试技巧

1. 打印完整 `messages` JSON（注意脱敏）  
2. 保存 `AgentTrace` 到文件  
3. live 失败时先用 mock 隔离是 schema 还是 runner 问题  
4. 对比 `finish_reason`: `tool_calls` vs `stop`  

## 7. 延伸阅读

- OpenAI Function Calling 官方文档  
- Day 20 Embedding + RAG 检索  
- Day 25 LangChain `bind_tools` 源码走读  

---

**讲师备注**：进阶班可现场演示「工具返回错误 → 模型自动改参数重试」。
