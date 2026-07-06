# Day 24 补充讲义 · SSE 与 CORS 深入

## 1. SSE 协议细节

### 1.1 字段说明

| 字段 | 含义 | 本课是否使用 |
|------|------|--------------|
| `data` | 消息负载 | ✅ JSON 字符串 |
| `event` | 事件类型 | ❌ 用 JSON 内 `event` 字段 |
| `id` | 事件 ID | ❌ |
| `retry` | 重连毫秒 | ❌ |

### 1.2 与 OpenAI API 对比

OpenAI `stream=True` 返回的也是 `data: {...}\n\n` 格式，但每行是 **completion chunk**，不是我们的业务事件封装。

本课封装：

```json
{"event": "delta", "delta": "文本片段"}
{"event": "done", "message_id": 42}
```

便于前端统一解析，也便于未来扩展 `tool_call` 事件。

### 1.3 缓冲问题

| 层级 | 风险 | 对策 |
|------|------|------|
| Python | 生成器未 flush | `StreamingResponse` 自动 chunked |
| Nginx | `proxy_buffering on` | `X-Accel-Buffering: no` |
| 浏览器 | 正常 | fetch 流式读取 |

## 2. CORS 深入

### 2.1 简单请求 vs 预检

`POST` + `Content-Type: application/json` → **预检请求**（OPTIONS）。

FastAPI `CORSMiddleware` 自动处理 OPTIONS 并返回：

```http
Access-Control-Allow-Origin: http://127.0.0.1:8080
Access-Control-Allow-Methods: DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT
```

### 2.2 credentials

`allow_credentials=True` 时，`Allow-Origin` 不能为 `*`，必须指定源。  
本课 session 在 localStorage，不依赖 Cookie，但为未来登录预留。

### 2.3 生产注意

- 仅允许已知前端域名  
- 勿在生产环境 `allow_methods=["*"]` 过于宽松（教学可放宽）  

## 3. fetch 读 SSE 代码剖析

### 3.1 为何需要 buffer

TCP chunk 可能把两条 SSE 消息拆断：

```text
data: {"event":"del
ta","delta":"a"}

data: {"event":"delta","delta":"b"}
```

`parseSSEBuffer` 以 `\n\n` 分割完整事件，剩余部分留到下次拼接。

### 3.2 TextDecoder stream 模式

```javascript
decoder.decode(value, { stream: true })
```

多字节 UTF-8 字符可能被拆在两个 chunk 中，`stream: true` 保证正确解码。

## 4. SQLAlchemy 2.0 要点

本课使用 `Mapped` + `mapped_column` 声明式风格：

```python
class ChatMessage(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
```

`get_db` 依赖注入保证请求结束关闭 Session，避免连接泄漏。

## 5. 排错命令速查

```bash
# 健康检查
curl -s http://127.0.0.1:8000/health | jq

# 非流式
curl -s -X POST http://127.0.0.1:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"你好","session_id":"curl-test"}' | jq

# 流式（看原始 SSE）
curl -N -X POST http://127.0.0.1:8000/api/chat/stream \
  -H 'Content-Type: application/json' \
  -d '{"message":"上海天气","session_id":"curl-sse"}'

# CORS 预检
curl -i -X OPTIONS http://127.0.0.1:8000/api/chat \
  -H 'Origin: http://127.0.0.1:8080' \
  -H 'Access-Control-Request-Method: POST'

# 查看 SQLite
sqlite3 data/chat_history.db "SELECT id, role, substr(content,1,40) FROM chat_messages;"
```

## 6. 延伸阅读

- [MDN: Server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [FastAPI StreamingResponse](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
- Day 16 `stream_demo.py` — 终端流式打字机

---

**版本**：v1.0 · SparkTech 培训中心
