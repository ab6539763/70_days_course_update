# Day 54 · LLaMA-Factory · 配置化微调实战

> **旁白**  
> 星火科技 · 大模型应用开发部 · **Phase4：垂直模型与私有化部署**  
项目代号延续 **星火智服**；Day 50 项目三答辩通过后，CTO 签发新 OKR：

> 「通用 API 成本占月预算 62%，客服话术一致性评分仅 71 分。  
>  第八周目标：**用 LoRA 微调 7B 级客服模型 + vLLM Docker 上线**，与现有 RAG 并存。」

---

## 今日学习地图

| 时段 | 主题 | 产出物 |
|------|------|--------|
| 09:00–10:30 | LLaMA-Factory 目录结构 | `llamafactory_configs/` |
| 10:30–12:00 | dataset_info 注册 | `dataset_info.json` |
| 14:00–16:00 | Mock Trainer | `mock_llamafactory_train.py` |
| 16:00–17:00 | 真机命令备忘 | `04_课堂讲义.md` |

## 衔接

- **前序**：[day53](../day53/)
- **后续**：[day55](../day55/)

## 文件清单

| 文件 | 用途 |
|------|------|
| [README.md](./README.md) | 学习地图 |
| [04_课堂讲义.md](./04_课堂讲义.md) | 主课 |
| [code/verify_day54.py](./code/verify_day54.py) | 验收 |

## 验收

```bash
cd day54/code
python3 verify_day54.py
```

---

**状态**：✅ Day 54 完整课件
