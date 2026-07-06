# Day 23 Code · FastAPI Chat API

## 依赖安装

```bash
cd day23/code
python3 -m venv ../.venv
source ../.venv/bin/activate   # Windows: ..\.venv\Scripts\activate
pip install -r requirements.txt
```

## 启动服务（uvicorn）

```bash
cd day23/code
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

或从 `day23/` 目录：

```bash
bash run.sh
```

## 自动文档

浏览器打开：

- Swagger UI：<http://127.0.0.1:8000/docs>
- ReDoc：<http://127.0.0.1:8000/redoc>

## 接口速查

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 服务信息 |
| GET | `/health` | 健康检查 |
| GET | `/items/{item_id}?q=` | 教学：路径参数 + 查询参数 |
| POST | `/api/chat` | **Chat 非流式**（对齐 Day 22） |
| GET | `/sessions/{id}/messages` | 调试：查看会话历史 |
| DELETE | `/sessions/{id}` | 清空会话 |

### POST /api/chat 示例

```bash
curl -s -X POST http://127.0.0.1:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"上海天气","session_id":"web-demo-001","stream":false}'
```

## 与 Day 22 前端联调

1. 终端 A：`cd day22 && bash preview.sh` → <http://127.0.0.1:8080>
2. 终端 B：`cd day23/code && uvicorn main:app --reload --port 8000`
3. 编辑 `day22/static/app.js`：
   - `USE_MOCK = false`
   - `API_BASE = 'http://127.0.0.1:8000'`
4. 刷新浏览器，发送「上海天气」验证真实 API 回复

## Mock 模式

默认 `SPARKTECH_MOCK=1`，无需 API Key。复制 `.env.example` 为 `.env` 可覆盖配置。

## 验收

```bash
python3 verify_day23.py
```

全部 `[OK]` 即通过。
