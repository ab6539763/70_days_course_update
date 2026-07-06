# Day 21 补充讲义 · Week 3 知识图谱（Day 15–20 速查）

> 测验前/订正时翻阅。每节 **3 分钟** 回忆检验。

---

## Day 15 · 多厂商 LLM + pytest

| 要点 | 速记 |
|------|------|
| 多态 | `OpenAIModel` / `QwenModel` 继承 `BaseModel`，只改 `generate()` |
| pytest | `def test_xxx(): assert ...`，`pytest -q` 一键回归 |
| token | 中英文混合约 1 字 ≈ 1–2 token；用 `messages[-N:]` 控成本 |
| 迁移 | Day 9 mock 类层次 → Day 15 换 HTTP 实现 |

```bash
pytest day15/tests -q
```

---

## Day 16 · temperature 与 max_tokens

```python
client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    temperature=0.7,      # 0=稳定 1=随机
    max_tokens=512,       # 生成上限
)
```

| 实验 | 建议值 |
|------|--------|
| 工单分类 | temperature=0 |
| 营销文案 | temperature=0.9 |
| 长文摘要 | max_tokens=1024 |

---

## Day 17 · Prompt 四要素

```text
【角色】你是星火智服售后助手。
【任务】根据工单内容给出处理建议。
【约束】200 字以内，禁止承诺退款。
【示例】
用户：物流慢
助手：建议查询物流单号...
```

模板工程：f-string 或 Jinja2 抽变量 `{{ticket_id}}`。

---

## Day 18 · JSON Mode + Rich

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    response_format={"type": "json_object"},
)
data = json.loads(response.choices[0].message.content)
```

Rich：`Console().print("[bold green]OK[/]")` 美化终端。

---

## Day 19 · Function Calling

工具 schema 示例：

```json
{
  "type": "function",
  "function": {
    "name": "get_weather",
    "description": "查询城市天气",
    "parameters": {
      "type": "object",
      "properties": {
        "city": {"type": "string"}
      },
      "required": ["city"]
    }
  }
}
```

执行环：解析 `tool_calls` → `execute` → `role: tool` 消息 → 再 `chat`。

---

## Day 20 · FastAPI + SSE + httpx

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

@app.post("/api/chat/stream")
async def chat_stream(req: ChatRequest):
    async def event_gen():
        async for chunk in llm.astream(messages):
            yield f"data: {json.dumps({'delta': chunk})}\n\n"
    return StreamingResponse(event_gen(), media_type="text/event-stream")
```

httpx：`async with client.stream("POST", url, json=body) as resp:`

---

## Day 15–20 → Day 21 映射表

| 专题 | Day 21 落点 |
|------|-------------|
| 多轮 messages | `ConversationSession` |
| temperature | `IntegratedClient` 构造参数 |
| Prompt | `SYSTEM_PROMPT` |
| JSON | 工具返回 `json.dumps` |
| Tools | `ToolRegistry` |
| SSE/流式 | `stream_tokens` / `stream_chat` |

---

## Day 22 预习清单

- [ ] HTML：`div` / `input` / `button` 语义  
- [ ] CSS：flex 布局、CSS 变量  
- [ ] JS：`fetch`、`addEventListener`、DOM 增删  
- [ ] 准备 3 条 CLI 对话截图给设计部  

---

**一句话**：Week 3 把「会调 API」升级为「会编排 Agent 内核」；Week 4 把它 **露到网页上**。
