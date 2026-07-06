# Day 12 补充讲义 · HTTP 与 LLM API 进阶

> 面向完成主课后的自学：通义千问切换、超时重试、与官方 SDK 对比、生产安全清单。

---

## 1. 通义千问（Qwen）免费 tier 切换

DeepSeek 与通义均提供 **OpenAI 兼容** HTTP 接口，`LLMClient` 只需改环境变量：

| 配置项 | DeepSeek | 通义千问（兼容模式） |
|--------|----------|----------------------|
| Base URL | `https://api.deepseek.com` | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| API Key 变量 | `DEEPSEEK_API_KEY` | `DASHSCOPE_API_KEY` |
| 默认模型 | `deepseek-chat` | `qwen-plus` 或 `qwen-turbo` |

`.env.example` 扩展（选做）：

```env
# DeepSeek（课程默认）
DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com

# 通义千问（可选）
# DASHSCOPE_API_KEY=
# DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

**课堂建议**：厂商文档以官网为准；endpoint 变更时只改 `base_url`，`messages` 格式不变。

---

## 2. 超时、重试与退避（预习 Day 13）

### 2.1 超时层次

```python
response = requests.post(url, json=payload, timeout=(5, 60))
#                                      连接超时 ↑  读取超时 ↑
```

| 阶段 | 建议 |
|------|------|
| 连接 | 5–10s |
| 读取 | 30–120s（长生成） |

### 2.2 简易重试（伪代码）

```python
import time

for attempt in range(3):
    try:
        response = requests.post(...)
        if response.status_code == 429:
            time.sleep(2 ** attempt)
            continue
        break
    except requests.Timeout:
        if attempt == 2:
            raise
        time.sleep(1)
```

| 状态码 | 是否重试 |
|--------|----------|
| 429 | 是，指数退避 |
| 500/502/503 | 可有限重试 |
| 401/403 | **否**，修 Key |
| 400 | **否**，修 payload |

---

## 3. requests vs 官方 openai SDK

```python
# requests（今日 — 看清 HTTP）
response = requests.post(f"{base_url}/v1/chat/completions", headers=..., json=payload)

# openai SDK（Day 15 对比）
from openai import OpenAI
client = OpenAI(api_key=key, base_url=base_url)
completion = client.chat.completions.create(model="deepseek-chat", messages=messages)
```

| 维度 | requests | SDK |
|------|----------|-----|
| 学习曲线 | 需懂 HTTP | 封装好 |
| 调试 | 完全透明 | 黑盒稍多 |
| 流式 | 手动解析 SSE | 内置 `stream=True` |
| 适用 | 教学、轻量 | 生产、复杂特性 |

张工意见：「先 requests 再 SDK，否则报错只会改模型名。」

---

## 4. curl 对照（排错利器）

```bash
curl https://api.deepseek.com/v1/chat/completions \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

Python 请求与 curl **一一对应**：URL、Headers、Body。

---

## 5. 响应字段延伸阅读

| 字段 | 含义 |
|------|------|
| `choices[0].finish_reason` | `stop` 正常结束；`length` 被 max_tokens 截断 |
| `usage.prompt_tokens` | 输入 token 数 |
| `usage.completion_tokens` | 输出 token 数 |
| `id` | 请求追踪 ID，找厂商客服用 |

---

## 6. 生产安全清单（王工版）

1. **密钥**：开发 `.env`、测试/生产 K8s Secret 或云密钥管理  
2. **网络**：生产出口 IP 白名单（若厂商支持）  
3. **审计**：记录 `request_id`、user_id、token 用量，不落库完整 prompt（涉敏时）  
4. **配额**：设置月度预算告警  
5. **内容**：敏感数据脱敏后再进 `messages`（星火智服工单号可留，密码不行）  

---

## 7. httpbin 替代（内网课堂）

若无法访问公网 httpbin：

```python
# 本地 mock server（选做）
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"echo": json.loads(body)}).encode())

# HTTPServer(("localhost", 8765), Handler).serve_forever()
```

下午 LLM 部分仍可用 **mock 模式** 完成验收。

---

## 8. 与 Day 9 BaseModel 的统一路线（Day 15 预告）

```text
  Day 12  LLMClient.chat()     ← 过程式封装，快速里程碑
  Day 15  DeepSeekModel(BaseModel)  ← 继承 generate()，多态路由恢复
```

今日先把 HTTP 打通；类层次回归时只替换 `generate()` 内部实现。

---

**一句话总结**：HTTP 是通用语言，OpenAI 兼容格式是方言；掌握 `POST + messages + choices`，换厂商只改 URL 和 Key。
