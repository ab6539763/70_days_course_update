# Day 52 · 数据集工程 · 工单转指令微调集

> **旁白**  
> 星火科技 · 大模型应用开发部 · **Phase4：垂直模型与私有化部署**  
项目代号延续 **星火智服**；Day 50 项目三答辩通过后，CTO 签发新 OKR：

> 「通用 API 成本占月预算 62%，客服话术一致性评分仅 71 分。  
>  第八周目标：**用 LoRA 微调 7B 级客服模型 + vLLM Docker 上线**，与现有 RAG 并存。」

---

## 今日学习地图

| 时段 | 主题 | 产出物 |
|------|------|--------|
| 09:00–10:30 | Alpaca / ShareGPT 格式 | `dataset_schema.py` |
| 10:30–12:00 | 工单清洗与脱敏 | `ticket_to_instruction.py` |
| 14:00–16:00 | 划分 train/val | `split_dataset.py` |
| 16:00–17:00 | 质量抽检 | `verify_day52.py` |

## 衔接

- **前序**：[day51](../day51/)
- **后续**：[day53](../day53/)

## 文件清单

| 文件 | 用途 |
|------|------|
| [README.md](./README.md) | 学习地图 |
| [04_课堂讲义.md](./04_课堂讲义.md) | 主课 |
| [code/verify_day52.py](./code/verify_day52.py) | 验收 |

## 验收

```bash
cd day52/code
python3 verify_day52.py
```

---

**状态**：✅ Day 52 完整课件
