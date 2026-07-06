# Day 57 · Docker 部署 · 阶段五收官（RAG + 微调推理联调）

> **旁白**  
> 星火科技 · 大模型应用开发部 · **Phase4：垂直模型与私有化部署**  
项目代号延续 **星火智服**；Day 50 项目三答辩通过后，CTO 签发新 OKR：

> 「通用 API 成本占月预算 62%，客服话术一致性评分仅 71 分。  
>  第八周目标：**用 LoRA 微调 7B 级客服模型 + vLLM Docker 上线**，与现有 RAG 并存。」  
> **今日终点**：`docker compose up` 一键拉起 **API 网关 + Mock vLLM + 健康检查**；有 Docker 环境的同学真跑，无 Docker 用 `verify_day57.py` mock 验收。

---

## 今日学习地图

| 时段 | 主题 | 产出物 |
|------|------|--------|
| 09:00–10:30 | Dockerfile 多阶段构建 | `deploy_stack/Dockerfile.api` |
| 10:30–12:00 | docker-compose 编排 | `docker-compose.yml` |
| 14:00–16:00 | 网关路由 RAG/微调 | `deploy_stack/api_gateway/` |
| 16:00–17:30 | 全栈验收 | `verify_day57.py` |

## 衔接

- **前序**：[day56](../day56/)
- **后续**：[day58](../day58/)（毕业设计启动）

## 快速开始

```bash
cd day57/code
python3 verify_day57.py          # 无 Docker
cd deploy_stack && docker compose up --build   # 有 Docker
```

---

**状态**：✅ Day 57 阶段五部署收官
