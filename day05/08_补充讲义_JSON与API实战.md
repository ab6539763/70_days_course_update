# Day 5 补充讲义 · JSON 与 API 实战衔接

> 本讲义在正课之后阅读，把今日 Mock 文件场景延伸到真实 HTTP 与 LLM API。

---

## 1. JSON 在 HTTP 中的位置

```text
  Client                          Server
    │                                │
    │  POST /api/employees           │
    │  Content-Type: application/json
    │  Body: {"page": 1}  ◀── JSON 字符串
    │ ─────────────────────────────▶ │
    │                                │
    │  200 OK                        │
    │  Body: {"code":200,"data":...} │
    │ ◀───────────────────────────── │
```

Day 5 你用 `json.load` 读文件；Day 12 用 `requests` 时：

```python
import json
import requests

resp = requests.get(url, timeout=30)
resp.raise_for_status()
data = resp.json()  # 等价于 json.loads(resp.text)
```

---

## 2. Content-Type 与编码

| 头 | 含义 |
|----|------|
| `Content-Type: application/json` | body 是 JSON 文本 |
| `charset=utf-8` | 字符集（常默认 UTF-8） |

写文件时我们显式 `encoding="utf-8"`，与 HTTP UTF-8 一致。

---

## 3. 大模型 API 请求体结构（预习）

OpenAI 兼容格式核心仍是 dict + JSON：

```json
{
  "model": "gpt-4o-mini",
  "messages": [
    {"role": "system", "content": "你是星火智服助手"},
    {"role": "user", "content": "如何导出员工 JSON？"}
  ],
  "temperature": 0.7,
  "stream": false
}
```

对应 Python：

```python
payload = {
    "model": "gpt-4o-mini",
    "messages": [
        {"role": "system", "content": "你是星火智服助手"},
        {"role": "user", "content": question},
    ],
    "temperature": 0.7,
    "stream": False,
}
body = json.dumps(payload, ensure_ascii=False)
```

**今日关联**：`messages` 是 **list[dict]**，与 `employees` 列表遍历同一套路。

---

## 4. 响应解析路径（Day 12 必背）

```python
content = data["choices"][0]["message"]["content"]
```

四层嵌套：根 dict → list → dict → dict → str。今日练 `.get()` 就是为这种路径防崩。

---

## 5. JSON 与配置文件

| 格式 | 优点 | 缺点 |
|------|------|------|
| JSON | 通用、API 同构 | 无注释 |
| YAML | 可读、有注释 | 缩进敏感（Day 10） |
| TOML | 适合 pyproject | 生态较小 |

企业内网配置常见 JSON；智服 Day 14 对话历史持久化也用 JSON 文件。

---

## 6. 性能与体积（了解）

- `separators=(',', ':')` 可压缩体积，去掉空格  
- 超大 JSON 用 `ijson` 流式解析（Day 28 文档场景）  
- 今日 Mock 仅 5 条，无需优化  

```python
compact = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
```

---

## 7. 安全提示

- **不要** `json.loads` 不可信来源后 `eval` 任意字段  
- 日志打印 JSON 时脱敏 `phone`、`id_card`（Day 52 合规课展开）  
- Mock 数据勿含真实员工 PII  

---

## 8. 排错速查表

| 报错 | 常见原因 |
|------|----------|
| `JSONDecodeError: Expecting property name` | 尾逗号、单引号 |
| `JSONDecodeError: Extra data` | 多个 JSON 拼在一个文件 |
| `TypeError: Object of type datetime is not JSON serializable` | 未转字符串 |
| `UnicodeDecodeError` | 打开文件未指定 utf-8 |
| `KeyError: 'employees'` | 未用 `.get()` 安全访问 |

---

## 9. 延伸阅读（本课程内）

- Day 6：把 `clean_employee` 抽成可测函数  
- Day 9：`try/except` 捕获 `JSONDecodeError`  
- Day 11：批量读目录下多个 JSON  
- Day 14：对话历史 `json.dump` 持久化  
- Day 23：Pydantic 替代手写清洗+校验  

---

**一句话总结**：Mock 文件是 Day 12 HTTP body 的替身；把 dict 与 JSON 四个 API 练熟，调 API 只是多了一步网络传输。
