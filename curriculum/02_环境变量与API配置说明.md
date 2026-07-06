# 环境变量命名说明（Day 12 ↔ Day 13/14）

## 为何出现两个变量名？

| 天数 | 变量 | 原因 |
|------|------|------|
| Day 12 | `DEEPSEEK_API_KEY` | 课堂首次对接 **DeepSeek 官方 API** |
| Day 13–14 | `OPENAI_API_KEY` | 使用 **OpenAI 兼容协议** 的通用客户端（DeepSeek/通义/本地 vLLM 均可） |

## 学员配置建议

**仅学 Day 12** 时，在 `day12/code/.env` 配置：

```env
DEEPSEEK_API_KEY=sk-...
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

**Day 13 项目一及以后**，在对应目录 `.env` 配置：

```env
OPENAI_API_KEY=sk-...          # DeepSeek Key 可直接填此处（兼容）
OPENAI_BASE_URL=https://api.deepseek.com/v1   # 若客户端支持 base_url
SPARKTECH_MOCK=1               # 强制 mock，答辩演示用
```

DeepSeek 的 Key 与 OpenAI 格式相同（`sk-` 开头），接入兼容客户端时**无需换厂商 SDK**。

## 安全提醒

- `.env` 已在各日 `.gitignore` / 根目录 `.gitignore` 忽略  
- 答辩演示优先使用 **mock 模式**，避免 Key 泄露  

---

## 阶段五（Day 51–57）微调与部署

| 变量 | 用途 | 示例 |
|------|------|------|
| `SPARKTECH_MOCK=1` | 无 GPU 时模拟训练/推理/网关 | 教学默认 |
| `CUDA_VISIBLE_DEVICES` | 指定训练 GPU | `0` |
| `VLLM_BASE_URL` | vLLM / Mock 推理地址 | `http://127.0.0.1:8100` |
| `HF_ENDPOINT` | HuggingFace 镜像（国内，选做） | `https://hf-mirror.com` |

**端口约定**（避免与前三项目冲突）：

| 服务 | 端口 |
|------|------|
| Project2 RAG | 8000 / 8080 |
| Project3 Agent | 8010 / 8088 |
| Mock vLLM | 8100 |
| Deploy Gateway | 8020 |

Day 57 Docker：`cd day57/code/deploy_stack && docker compose up --build`
