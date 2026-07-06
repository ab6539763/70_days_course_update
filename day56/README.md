# Day 56 · vLLM 推理服务 · OpenAI 兼容 API

> **旁白**  
> 星火科技 · 大模型应用开发部 · **Phase4：垂直模型与私有化部署**  
项目代号延续 **星火智服**；Day 50 项目三答辩通过后，CTO 签发新 OKR：

> 「通用 API 成本占月预算 62%，客服话术一致性评分仅 71 分。  
>  第八周目标：**用 LoRA 微调 7B 级客服模型 + vLLM Docker 上线**，与现有 RAG 并存。」

---

## 今日学习地图

| 时段 | 主题 | 产出物 |
|------|------|--------|
| 09:00–10:30 | vLLM 架构 | `04_课堂讲义.md` |
| 10:30–12:00 | Mock OpenAI Server | `mock_vllm_server.py` |
| 14:00–16:00 | 客户端与压测 | `openai_client.py` |
| 16:00–17:00 | 延迟 benchmark | `benchmark_latency.py` |

## 衔接

- **前序**：[day55](../day55/)
- **后续**：[day57](../day57/)

## 文件清单

| 文件 | 用途 |
|------|------|
| [README.md](./README.md) | 学习地图 |
| [04_课堂讲义.md](./04_课堂讲义.md) | 主课 |
| [code/verify_day56.py](./code/verify_day56.py) | 验收 |

## 验收

```bash
cd day56/code
python3 verify_day56.py
```

---

**状态**：✅ Day 56 完整课件
