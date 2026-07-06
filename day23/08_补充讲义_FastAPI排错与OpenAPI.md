# Day 23 补充讲义 · FastAPI 排错与 OpenAPI 速查

> 联调卡住时翻本节；配合 Chrome DevTools Network 与 uvicorn 终端日志。

---

## 1. HTTP 状态码速查

| 状态码 | 含义 | Day 23 典型场景 |
|--------|------|-----------------|
| 200 | 成功 | `POST /api/chat` 正常 |
| 422 | 校验失败 | `message` 空白、类型错误 |
| 404 | 未找到 | 路径拼写错误 `/api/chats` |
| 501 | 未实现 | `stream: true` |
| 500 | 服务器错误 | 未捕获异常，查 uvicorn 日志 |

---

## 2. 422 排错清单

### 2.1 读 detail 数组

```json
{
  "detail": [
    {
      "type": "json_invalid",
      "loc": ["body", 12],
      "msg": "JSON decode error",
      "input": {}
    }
  ]
}
```

| loc | 含义 |
|-----|------|
| `["body"]` | 整个 body 有问题（JSON 语法） |
| `["body", "message"]` | `message` 字段 |
| `["query", "q"]` | 查询参数 |

### 2.2 常见触发

| 请求 | 结果 |
|------|------|
| body 不是 JSON | 422 `json_invalid` |
| 缺 `message` | 422 `missing` |
| `message: 123`（数字） | 422 `string_type` |
| `message: ""` | 422 `string_too_short` 或 validator |

### 2.3 curl 正确写法

```bash
curl -X POST http://127.0.0.1:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"hi","session_id":"s1","stream":false}'
```

`-d` 必须是 **合法 JSON 字符串**；单引号包裹避免 shell 转义问题。

---

## 3. CORS 深度说明

### 3.1 谁 enforcement

| 组件 | 是否检查 CORS |
|------|---------------|
| 浏览器 JS | ✅ |
| curl / Postman | ❌ |
| Python requests | ❌ |
| 服务器间调用 | ❌ |

因此：**curl 通、浏览器不通** → 几乎一定是 CORS。

### 3.2 正确配置模板

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8080",
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
```

教学可用 `["*"]`；生产用白名单。

### 3.3 中间件顺序

`add_middleware` 后添加的 **先执行**（洋葱模型）。CORS 通常 **最先** 加，确保 OPTIONS 预检也被处理。

---

## 4. uvicorn 启动排错

| 错误 | 原因 | 解决 |
|------|------|------|
| `Address already in use` | 8000 占用 | `lsof -i :8000` / 换端口 |
| `Error loading ASGI app` | 模块路径错 | 确认 `main:app` 与 cwd |
| `No module named 'fastapi'` | 未装依赖 | `pip install -r requirements.txt` |
| 改代码不生效 | 未加 `--reload` | 开发时加 `--reload` |

推荐启动：

```bash
cd day23/code
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

---

## 5. OpenAPI / Swagger 使用技巧

### 5.1 三个文档 URL

| URL | 格式 |
|-----|------|
| `/docs` | Swagger UI（可试调） |
| `/redoc` | ReDoc（阅读友好） |
| `/openapi.json` | 原始 JSON Schema |

### 5.2 用 /docs 调试 POST

1. 展开 `POST /api/chat`  
2. Try it out  
3. 编辑 Request body  
4. Execute  
5. 查看 Response body 与 Code  

### 5.3 导出给前端

把 `/openapi.json` 发给前端同学生成 TypeScript 类型（选做工具：`openapi-typescript`）。

---

## 6. TestClient 单测模式

`verify_day23.py` 使用：

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
res = client.post("/api/chat", json={...})
```

优点：无需启动 uvicorn，CI 友好。  
注意：TestClient 同步调用 async 路由时 FastAPI 内部处理事件循环。

---

## 7. Pydantic v2 备忘

| v1 | v2 |
|----|-----|
| `@validator` | `@field_validator` |
| `class Config` | `model_config = ConfigDict(...)` |
| `.dict()` | `.model_dump()` |
| `.json()` | `.model_dump_json()` |

本课程统一 **Pydantic v2**。

---

## 8. 环境变量

| 变量 | 默认 | 说明 |
|------|------|------|
| `SPARKTECH_MOCK` | `1` | `0` 尝试 live |
| `OPENAI_API_KEY` | 空 | live 必需 |
| `OPENAI_MODEL` | `gpt-4o-mini` | 模型名 |
| `OPENAI_BASE_URL` | OpenAI 官方 | 兼容代理 |

加载顺序：`code/.env` → `day23/.env` → 系统环境。

---

## 9. 日志与调试

### 9.1 临时打印

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 9.2 查看会话历史

```bash
curl -s http://127.0.0.1:8000/sessions/web-demo-001/messages | python3 -m json.tool
```

### 9.3 清空会话

```bash
curl -X DELETE http://127.0.0.1:8000/sessions/web-demo-001
```

---

## 10. 与 Day 24 衔接预告

| 主题 | Day 23 | Day 24 |
|------|--------|--------|
| 非流式 | ✅ | ✅ |
| 流式 SSE | 501 | 实现 |
| 前端 typewriter | mock 假流 | 真 token 流 |
| EventSource | 注释占位 | 启用 |

今日排错能力（CORS、422、契约字段）是 Day 24 联调的 **前置技能**。

---

**速查口诀**：**422 看 detail，跨域加 CORS，curl 通浏览器不通就找中间件，契约三字 reply session tools。**
