# Day 27 补充讲义 · Memory 策略选型

## 1. 何时用哪种 Memory

| 场景 | 推荐 |
|------|------|
| 单元测试 / 课堂 demo | `ChatMessageHistory` 内存 |
| 客服 5～10 轮短会话 | `WindowChatMessageHistory` |
| 长咨询 / 工单跟进 | Summary + Window 组合 |
| 生产 Web / CLI 重启保留 | `SQLChatMessageHistory` 或 Redis |

## 2. RunnableWithMessageHistory 参数

| 参数 | 说明 |
|------|------|
| `input_messages_key` | 单字符串输入字段名 |
| `history_messages_key` | 历史占位字段名 |
| `output_messages_key` | 默认输出写回 ai 消息 |

多模态或工具调用场景可能需自定义 `history_factory` 与 `message` 转换。

## 3. 与旧版 Memory 类关系

LangChain 0.3 推荐 **RunnableWithMessageHistory** 替代：

- `ConversationBufferMemory`  
- `ConversationBufferWindowMemory`  
- `ConversationSummaryMemory`  

旧类仍存在于 `langchain.memory`，新课程 **不优先使用**。

## 4. Token 控制进阶（预告）

- `trim_messages` 按 token 裁剪  
- `ConversationTokenBufferMemory` 思路  
- 与 Embedding 检索结合 → RAG Memory（Week 6+）

## 5. 排错

| 现象 | 检查 |
|------|------|
| 每轮都像首轮 | `session_id` 是否传入 config |
| history 不增长 | `output_messages_key` / 链输出类型 |
| SQLite 锁 | 单进程 SQLite 路径是否可写 |
| Window 未裁剪 | `add_message` 是否调用 `_trim` |

## 6. 参考

- LangChain Memory: https://python.langchain.com/docs/concepts/memory/  
- RunnableWithMessageHistory: https://python.langchain.com/api_reference/core/runnables/langchain_core.runnables.history.RunnableWithMessageHistory.html  
