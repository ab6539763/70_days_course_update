#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate Day 51-57 courseware for fine-tuning & deployment phase."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def w(path: str, content: str) -> None:
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.strip() + "\n", encoding="utf-8")
    print(f"  wrote {path}")


# ---------------------------------------------------------------------------
# Shared snippets
# ---------------------------------------------------------------------------

BIZ_INTRO = """
星火科技 · 大模型应用开发部 · **Phase4：垂直模型与私有化部署**  
项目代号延续 **星火智服**；Day 50 项目三答辩通过后，CTO 签发新 OKR：

> 「通用 API 成本占月预算 62%，客服话术一致性评分仅 71 分。  
>  第八周目标：**用 LoRA 微调 7B 级客服模型 + vLLM Docker 上线**，与现有 RAG 并存。」
"""

VERIFY_HEADER = '''# -*- coding: utf-8 -*-
"""Day {day} 验收脚本 —— SPARKTECH_MOCK=1 无需 GPU / API Key。"""

from __future__ import annotations

import os
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE_DIR))
os.environ.setdefault("SPARKTECH_MOCK", "1")


def ok(msg: str) -> None:
    print(f"[OK] {{msg}}")


def fail(msg: str) -> None:
    print(f"[FAIL] {{msg}}")
    raise SystemExit(1)


def main() -> None:
    print("=== Day {day} verify ===")
'''

RUN_SH = """#!/bin/bash
set -e
cd "$(dirname "$0")/code"
export SPARKTECH_MOCK=1
python3 verify_day{day}.py
echo ""
echo "✅ Day {day} 验收通过"
"""


def day_readme(day: int, title: str, schedule: list[tuple[str, str, str]], prev: str, nxt: str) -> str:
    rows = "\n".join(f"| {a} | {b} | {c} |" for a, b, c in schedule)
    files = "\n".join(f"| [{n}](./{n}) | {d} |" for n, d in [
        ("README.md", "学习地图"),
        ("04_课堂讲义.md", "主课"),
        (f"code/verify_day{day}.py", "验收"),
    ])
    return f"""# Day {day} · {title}

> **旁白**  
> {BIZ_INTRO.strip()}

---

## 今日学习地图

| 时段 | 主题 | 产出物 |
|------|------|--------|
{rows}

## 衔接

- **前序**：[{prev}](../{prev}/)
- **后续**：[{nxt}](../{nxt}/)

## 文件清单

| 文件 | 用途 |
|------|------|
{files}

## 验收

```bash
cd day{day:02d}/code
python3 verify_day{day}.py
```

---

**状态**：✅ Day {day} 完整课件
"""


def std_md(day: int, kind: str, title: str, body: str) -> str:
    return f"# Day {day} {kind} · {title}\n\n{body.strip()}\n"


# ---------------------------------------------------------------------------
# DAY 51
# ---------------------------------------------------------------------------

def gen_day51() -> None:
    d = 51
    w(f"day{d}/README.md", day_readme(
        d, "微调概论 · RAG / Prompt / SFT 选型",
        [
            ("09:00–10:30", "微调 vs RAG vs Prompt", "`compare_approaches.py`"),
            ("10:30–12:00", "SFT / RLHF / DPO 概念", "`04_课堂讲义.md`"),
            ("14:00–15:30", "企业微调决策树", "`finetune_decision_tree.py`"),
            ("15:30–17:00", "星火智服 Phase4 OKR", "`verify_day51.py`"),
        ],
        "day50", "day52",
    ))
    w(f"day{d}/01_业务背景.md", std_md(d, "业务背景", "CTO 下达降本与话术一致性 OKR", """
## 1. 经营数据（周一晨会）

| 指标 | 当前 | 目标（Day 57） |
|------|------|----------------|
| 月 API 费用 | ¥128,000 | ↓ 35% |
| 客服话术一致性（人工抽检） | 71% | ≥ 90% |
| 首 token 延迟 P95 | 1.8s | ≤ 800ms（私有化后） |
| 敏感数据外发 | 100% 经公有云 | 核心话术模型内网 |

张工白板：**「不是不用 RAG，是 RAG 检索 + 微调小模型写答案，分工明确。」**

## 2. 三种路线对比

```text
用户问题
  ├─ 知识在文档里且常更新 → RAG（Project2 已有）
  ├─ 固定话术/风格/术语 → SFT + LoRA（本周主线）
  └─ 偶发复杂推理 → 保留大模型 API 作 fallback
```

## 3. 今日交付

- 团队共识文档：何时微调、何时不微调  
- `compare_approaches.py` 输出决策建议  
- `finetune_decision_tree.py` 可嵌入评审会

---

*需求见 [02_需求文档.md](./02_需求文档.md)*
"""))
    w(f"day{d}/02_需求文档.md", std_md(d, "需求文档", "Phase4 技术选型 PRD 节选", """
## 用户故事

| ID | 角色 | 故事 | 优先级 |
|----|------|------|--------|
| US-51-01 | 产品经理 | 我要一张决策表，判断新需求走 RAG 还是微调 | P0 |
| US-51-02 | 架构师 | 我要评估全量微调 vs LoRA 的成本 | P0 |
| US-51-03 | 合规 | 我要确认训练数据脱敏策略 | P1 |

## 验收标准

- [ ] `compare_approaches(scenario)` 返回 `rag|finetune|prompt|hybrid`  
- [ ] 决策树覆盖 ≥ 8 种业务场景  
- [ ] 文档列出 SFT / RLHF / DPO 适用边界  
- [ ] `verify_day51.py` 全绿
"""))
    w(f"day{d}/03_架构与设计.md", std_md(d, "架构与设计", "Phase4 技术栈总览", """
## 1. 目标架构（Day 57 终点）

```mermaid
flowchart TB
    User[用户/客服坐席] --> GW[API Gateway FastAPI]
    GW --> RAG[Project2 RAG 服务]
    GW --> VLLM[vLLM 微调模型]
    GW --> API[公有云大模型 Fallback]
    RAG --> Chroma[(Chroma)]
    VLLM --> LoRA[LoRA Adapter]
```

## 2. 本周模块划分

| 天 | 模块 |
|----|------|
| 51 | 选型与概念 |
| 52 | 数据集 |
| 53 | LoRA 原理 |
| 54 | LLaMA-Factory 训练 |
| 55 | 离线评估 |
| 56 | vLLM 推理 |
| 57 | Docker Compose 联调 |

## 3. 环境约定

| 变量 | 含义 |
|------|------|
| `SPARKTECH_MOCK=1` | 无 GPU 时模拟训练/推理 |
| `CUDA_VISIBLE_DEVICES` | 有 GPU 学员真训 |
| `VLLM_BASE_URL` | 推理服务地址 |
"""))
    w(f"day{d}/04_课堂讲义.md", std_md(d, "课堂讲义", "微调概论与选型", """
## 第一章 · 为什么企业要做微调（09:00–10:00）

**微调（Fine-tuning）**：在预训练权重上继续训练，让模型适应特定任务或领域。

| 手段 | 优点 | 缺点 |
|------|------|------|
| Prompt | 零训练、迭代快 | 长 prompt 贵、风格不稳 |
| RAG | 知识可更新、可溯源 | 不改善「怎么说」 |
| SFT | 风格稳、术语准 | 需数据与算力 |
| RLHF/DPO | 对齐人类偏好 | 成本高、工程复杂 |

星火智服选型：**RAG 查政策 + LoRA 模型写客服话术**。

## 第二章 · SFT 数据形态（10:00–11:00）

单轮指令格式（Alpaca）：

```json
{"instruction": "用户问退款多久到账", "input": "", "output": "您好，退款一般3-5个工作日..."}
```

多轮 ShareGPT 格式用于对话连贯性（Day 52 详讲）。

## 第三章 · 全量微调 vs 参数高效（11:00–12:00）

全量微调更新全部权重；**LoRA** 只训练低秩适配器，显存需求降一个数量级。

```text
7B 全量 FP16 ≈ 14GB+ 显存
7B + LoRA r=8  ≈ 12GB 可训（QLoRA 更低）
```

## 第四章 · 决策树实操（14:00–17:00）

运行：

```bash
cd day51/code
python3 compare_approaches.py
python3 finetune_decision_tree.py
python3 verify_day51.py
```

**课堂讨论**：「新产品 FAQ 每周变」应走 RAG；「统一道歉信语气」应走 SFT。

## 小结

明日 Day 52：从工单系统导出数据，清洗为 `train.jsonl`。
"""))
    w(f"day{d}/05_流程图与示意图.md", std_md(d, "流程图", "微调选型", """
```mermaid
flowchart TD
    Q[新需求] --> U{知识是否频繁更新?}
    U -->|是| RAG[RAG 检索增强]
    U -->|否| S{是否固定话术风格?}
    S -->|是| FT[LoRA SFT]
    S -->|否| P[Prompt 优化]
    FT --> H[Hybrid: RAG + 微调模型]
    RAG --> H
```
"""))
    w(f"day{d}/06_课后作业.md", std_md(d, "课后作业", "", """
## 必做

1. 为星火智服列举 5 个「应微调」和 5 个「应 RAG」场景。  
2. 运行 `compare_approaches.py`，截图 3 条不同场景输出。  
3. 阅读 `finetune_decision_tree.py`，补充第 9 条规则。

## 选做

写一篇 500 字「为什么不建议新手上来就 RLHF」。
"""))
    w(f"day{d}/07_作业参考答案.md", std_md(d, "作业参考答案", "", """
## 场景分类参考

**宜微调**：标准致歉模板、工单分类口吻、品牌称呼、简短确认语、合规免责声明。  
**宜 RAG**：退款政策原文、产品价格、活动规则、API 文档、版本更新日志。

## 第 9 条规则示例

若 `scenario.tags` 含 `realtime_price` → 强制 `rag`（价格实时变化不能写进权重）。
"""))
    w(f"day{d}/08_补充讲义_微调术语表.md", std_md(d, "补充讲义", "术语速查", """
| 术语 | 解释 |
|------|------|
| SFT | Supervised Fine-Tuning 有监督微调 |
| LoRA | Low-Rank Adaptation 低秩适配 |
| QLoRA | 量化 + LoRA |
| RLHF | 人类反馈强化学习 |
| DPO | 直接偏好优化 |
| PEFT | 参数高效微调总称 |
| Base model | 基座模型如 Qwen2.5-7B |
| Adapter | 可插拔微调权重 |
"""))
    w(f"day{d}/code/compare_approaches.py", '''# -*- coding: utf-8 -*-
"""Day 51 · RAG / Prompt / Fine-tune 场景对比。"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Approach(str, Enum):
    RAG = "rag"
    FINETUNE = "finetune"
    PROMPT = "prompt"
    HYBRID = "hybrid"


@dataclass
class Scenario:
    name: str
    knowledge_updates: bool
    style_fixed: bool
    needs_citation: bool
    complexity: str  # low|medium|high


def recommend(s: Scenario) -> Approach:
  if s.needs_citation or s.knowledge_updates:
      if s.style_fixed:
          return Approach.HYBRID
      return Approach.RAG
  if s.style_fixed:
      return Approach.FINETUNE
  if s.complexity == "high":
      return Approach.PROMPT
  return Approach.PROMPT


SCENARIOS = [
    Scenario("退款政策咨询", True, False, True, "medium"),
    Scenario("标准致歉话术", False, True, False, "low"),
    Scenario("多步投诉推理", False, False, False, "high"),
    Scenario("产品规格+品牌语气", True, True, True, "medium"),
]


def main() -> None:
    print("Day 51 · compare_approaches")
    for s in SCENARIOS:
        rec = recommend(s)
        print(f"  {s.name:20s} -> {rec.value}")


if __name__ == "__main__":
    main()
''')
    w(f"day{d}/code/finetune_decision_tree.py", '''# -*- coding: utf-8 -*-
"""Day 51 · 可编程微调决策树。"""

from __future__ import annotations

from typing import Any


RULES: list[tuple[str, callable]] = [
    ("knowledge_updates", lambda ctx: "rag" if ctx.get("knowledge_updates") else None),
    ("needs_citation", lambda ctx: "rag" if ctx.get("needs_citation") else None),
    ("style_fixed", lambda ctx: "finetune" if ctx.get("style_fixed") else None),
    ("high_complexity", lambda ctx: "prompt" if ctx.get("complexity") == "high" else None),
    ("hybrid_brand_rag", lambda ctx: "hybrid" if ctx.get("style_fixed") and ctx.get("knowledge_updates") else None),
]


def decide(ctx: dict[str, Any]) -> str:
    for name, fn in RULES:
        result = fn(ctx)
        if result:
            return result
    return "prompt"


def main() -> None:
    tests = [
        {"name": "政策+引用", "knowledge_updates": True, "needs_citation": True},
        {"name": "致歉模板", "style_fixed": True},
        {"name": "复杂推理", "complexity": "high"},
    ]
    for t in tests:
        label = t.pop("name")
        print(f"  {label}: {decide(t)}")


if __name__ == "__main__":
    main()
''')
    w(f"day{d}/code/verify_day51.py", VERIFY_HEADER.format(day=d) + """
    from compare_approaches import recommend, SCENARIOS, Approach
    from finetune_decision_tree import decide

    for s in SCENARIOS:
        r = recommend(s)
        if r not in Approach:
            fail(f"invalid approach {r}")
    ok("compare_approaches")

    if decide({"style_fixed": True}) != "finetune":
        fail("decision tree style_fixed")
    ok("finetune_decision_tree")

    print("=== ALL PASSED ===")


if __name__ == "__main__":
    main()
""")
    w(f"day{d}/run.sh", RUN_SH.format(day=d))


# ---------------------------------------------------------------------------
# DAY 52 - dataset
# ---------------------------------------------------------------------------

def gen_day52() -> None:
    d = 52
    w(f"day{d}/README.md", day_readme(
        d, "数据集工程 · 工单转指令微调集",
        [
            ("09:00–10:30", "Alpaca / ShareGPT 格式", "`dataset_schema.py`"),
            ("10:30–12:00", "工单清洗与脱敏", "`ticket_to_instruction.py`"),
            ("14:00–16:00", "划分 train/val", "`split_dataset.py`"),
            ("16:00–17:00", "质量抽检", "`verify_day52.py`"),
        ],
        "day51", "day53",
    ))
    for name, title, body in [
        ("01_业务背景", "数据组交付 2000 条历史工单", "法务要求脱敏后方可进训练集；今日产出 `data/train.jsonl` 与 `data/val.jsonl`。"),
        ("02_需求文档", "数据集 PRD", "字段：instruction/input/output；脱敏手机邮箱；train:val=9:1；≥100 条样本。"),
        ("03_架构与设计", "数据流水线", "```text\nraw_tickets.json → 清洗 → 脱敏 → 格式校验 → split → jsonl```"),
        ("04_课堂讲义", "数据集工程", "## 清洗\n- 去掉系统消息\n- 合并连续客服回复\n\n## 脱敏\n- 手机/身份证/邮箱\n\n## 质量\n- 重复率 < 5%\n- 平均 output 长度 50-300 字"),
        ("05_流程图与示意图", "数据流", "```mermaid\nflowchart LR\n  T[工单] --> C[清洗] --> M[脱敏] --> J[jsonl]\n```"),
        ("06_课后作业", "作业", "扩充 `raw_tickets.json` 至 50 条；手写 10 条高质量致歉样本。"),
        ("07_作业参考答案", "参考答案", "致歉样本应包含：称呼、歉意、原因、下一步、落款。"),
        ("08_补充讲义_数据合规清单", "合规", "禁止含：完整身份证号、银行卡、密码、未公开商业条款。"),
    ]:
        kind = name.split("_")[0]
        w(f"day{d}/{name}.md", std_md(d, kind, title, body))

    samples = [
        {"instruction": "客户催促退款进度", "input": "订单号已提供，等待3天", "output": "您好，已为您加急查询，预计1个工作日内到账，请留意短信。"},
        {"instruction": "客户投诉响应慢", "input": "", "output": "非常抱歉让您久等，我们已升级处理，专员将在30分钟内回电。"},
        {"instruction": "询问发票开具", "input": "企业抬头", "output": "您好，电子发票将在付款后24小时内发送至您邮箱，请确认抬头无误。"},
    ]
    w(f"day{d}/code/data/raw_tickets.json", json.dumps([
        {"ticket_id": "T001", "user": "我要退款", "agent": "好的帮您查", "category": "refund"},
        {"ticket_id": "T002", "user": "太慢了", "agent": "抱歉加急", "category": "complaint"},
    ], ensure_ascii=False, indent=2))
    w(f"day{d}/code/dataset_schema.py", '''# -*- coding: utf-8 -*-
"""Day 52 · Alpaca 格式校验。"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REQUIRED = ("instruction", "output")


@dataclass
class ValidationResult:
    ok: bool
    errors: list[str]


def validate_record(rec: dict[str, Any]) -> ValidationResult:
    errors: list[str] = []
    for k in REQUIRED:
        if k not in rec or not str(rec[k]).strip():
            errors.append(f"missing_{k}")
    if "input" not in rec:
        errors.append("missing_input_key")
    return ValidationResult(len(errors) == 0, errors)


def validate_jsonl(path: Path) -> ValidationResult:
    errors: list[str] = []
    if not path.is_file():
        return ValidationResult(False, ["file_not_found"])
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        rec = json.loads(line)
        vr = validate_record(rec)
        if not vr.ok:
            errors.append(f"line{i}:{','.join(vr.errors)}")
    return ValidationResult(len(errors) == 0, errors)
''')
    w(f"day{d}/code/ticket_to_instruction.py", '''# -*- coding: utf-8 -*-
"""Day 52 · 工单转 Alpaca 指令数据。"""

from __future__ import annotations

import json
import re
from pathlib import Path

RAW = Path(__file__).parent / "data" / "raw_tickets.json"
PHONE_RE = re.compile(r"1[3-9]\\d{9}")
EMAIL_RE = re.compile(r"[\\w.-]+@[\\w.-]+\\.\\w+")


def desensitize(text: str) -> str:
    text = PHONE_RE.sub("[PHONE]", text)
    text = EMAIL_RE.sub("[EMAIL]", text)
    return text


def ticket_to_record(ticket: dict) -> dict:
    user = desensitize(ticket.get("user", ""))
    agent = desensitize(ticket.get("agent", ""))
    return {
        "instruction": f"作为星火智服客服回复：{user}",
        "input": "",
        "output": agent,
        "meta": {"ticket_id": ticket.get("ticket_id"), "category": ticket.get("category")},
    }


def convert(raw_path: Path | None = None) -> list[dict]:
    path = raw_path or RAW
    tickets = json.loads(path.read_text(encoding="utf-8"))
    return [ticket_to_record(t) for t in tickets]


def main() -> None:
    recs = convert()
    for r in recs:
        print(json.dumps(r, ensure_ascii=False))


if __name__ == "__main__":
    main()
''')
    w(f"day{d}/code/split_dataset.py", '''# -*- coding: utf-8 -*-
"""Day 52 · train/val 划分。"""

from __future__ import annotations

import json
import random
from pathlib import Path

from ticket_to_instruction import convert

DATA_DIR = Path(__file__).parent / "data"
SEED = 42


def split(records: list[dict], val_ratio: float = 0.1) -> tuple[list, list]:
    rng = random.Random(SEED)
    shuffled = records[:]
    rng.shuffle(shuffled)
    n_val = max(1, int(len(shuffled) * val_ratio))
    return shuffled[n_val:], shuffled[:n_val]


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in records:
            row = {k: r[k] for k in ("instruction", "input", "output") if k in r}
            f.write(json.dumps(row, ensure_ascii=False) + "\\n")


def build() -> tuple[Path, Path]:
    records = convert()
    # 扩充样本以满足训练集规模演示
    templates = [
        {"instruction": "客户催促退款进度", "input": "", "output": "您好，已加急处理，1个工作日内到账。"},
        {"instruction": "客户投诉响应慢", "input": "", "output": "非常抱歉，已升级专员30分钟内回电。"},
    ]
    records.extend(templates)
    train, val = split(records)
    train_path = DATA_DIR / "train.jsonl"
    val_path = DATA_DIR / "val.jsonl"
    write_jsonl(train_path, train)
    write_jsonl(val_path, val)
    return train_path, val_path


if __name__ == "__main__":
    t, v = build()
    print(f"train={t} val={v}")
''')
    w(f"day{d}/code/verify_day52.py", VERIFY_HEADER.format(day=d) + """
    from pathlib import Path
    from dataset_schema import validate_jsonl
    from split_dataset import build

    train, val = build()
    if not train.is_file() or not val.is_file():
        fail("jsonl not created")
    for p in (train, val):
        vr = validate_jsonl(p)
        if not vr.ok:
            fail(f"validate {p.name}: {vr.errors}")
    ok("train/val jsonl")

    if sum(1 for _ in train.open() if _.strip()) < 2:
        fail("train too small")
    ok("dataset size")

    print("=== ALL PASSED ===")


if __name__ == "__main__":
    main()
""")
    w(f"day{d}/run.sh", RUN_SH.format(day=d))


def gen_day53() -> None:
    d = 53
    w(f"day{d}/README.md", day_readme(
        d, "LoRA / QLoRA · 参数高效微调原理",
        [
            ("09:00–10:30", "低秩分解直觉", "`lora_math_demo.py`"),
            ("10:30–12:00", "rank / alpha / target_modules", "`lora_config_explainer.py`"),
            ("14:00–16:00", "Mock 训练循环", "`lora_mock_train.py`"),
            ("16:00–17:00", "验收", "`verify_day53.py`"),
        ],
        "day52", "day54",
    ))
    bodies = {
        "01_业务背景": ("显存预算", "运维只批 24GB 单卡；全量微调不可行，LoRA r=8 为默认方案。"),
        "02_需求文档": ("LoRA 配置 PRD", "输出 `configs/lora_sparktech.yaml` 字段说明；mock 训练可打印 loss 曲线。"),
        "03_架构与设计": ("LoRA 插入点", "典型 target：`q_proj,v_proj`；推理时 `base + adapter` 合并或热加载。"),
        "04_课堂讲义": ("LoRA 原理", "## 公式\nΔW = B·A，r << d\n\n## QLoRA\n4bit 基座 + LoRA 训练\n\n## 超参\n- r: 8-64\n- alpha: 通常 2r\n- dropout: 0.05"),
        "05_流程图与示意图": ("训练流", "```mermaid\nflowchart LR\n  B[Base 7B] --> L[LoRA Adapter]\n  D[Dataset] --> T[Train only LoRA]\n```"),
        "06_课后作业": ("", "改 r=4/16 各跑一次 mock，记录 loss 差异。"),
        "07_作业参考答案": ("", "r 过小欠拟合，过大易过拟合显存增。"),
        "08_补充讲义_LoRA超参表": ("超参", "| r | 适用 |\n|---|------|\n| 4 | 风格轻量 |\n| 8 | 默认 |\n| 16+ | 复杂领域 |"),
    }
    for fname, (title, body) in bodies.items():
        kind = fname.split("_")[0]
        w(f"day{d}/{fname}.md", std_md(d, kind, title, body))

    w(f"day{d}/code/lora_math_demo.py", '''# -*- coding: utf-8 -*-
"""Day 53 · LoRA 低秩直觉演示（纯 numpy）。"""

from __future__ import annotations


def lora_delta_demo(d: int = 64, r: int = 4) -> dict:
    full_params = d * d
    lora_params = d * r + r * d
    return {
        "d": d,
        "r": r,
        "full_params": full_params,
        "lora_params": lora_params,
        "ratio": round(lora_params / full_params, 4),
    }


def main() -> None:
    for r in (4, 8, 16):
        info = lora_delta_demo(r=r)
        print(f"r={r} params_ratio={info['ratio']}")


if __name__ == "__main__":
    main()
''')
    w(f"day{d}/code/lora_config_explainer.py", '''# -*- coding: utf-8 -*-
"""Day 53 · LoRA 配置解释器。"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json


@dataclass
class LoRAConfig:
    r: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.05
    target_modules: tuple[str, ...] = ("q_proj", "v_proj")
    bias: str = "none"

    def explain(self) -> str:
        return (
            f"rank={self.r}, alpha={self.lora_alpha} (scale={self.lora_alpha/self.r}), "
            f"targets={list(self.target_modules)}"
        )


def save_config(path: Path) -> LoRAConfig:
    cfg = LoRAConfig()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(cfg), indent=2), encoding="utf-8")
    return cfg


if __name__ == "__main__":
    cfg = save_config(Path(__file__).parent / "configs" / "lora_sparktech.json")
    print(cfg.explain())
''')
    w(f"day{d}/code/lora_mock_train.py", '''# -*- coding: utf-8 -*-
"""Day 53 · 模拟 LoRA 训练（无 GPU）。"""

from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class TrainLog:
    epoch: int
    step: int
    loss: float


def mock_train(*, epochs: int = 3, steps_per_epoch: int = 5) -> list[TrainLog]:
    logs: list[TrainLog] = []
    loss = 2.5
    for ep in range(1, epochs + 1):
        for step in range(1, steps_per_epoch + 1):
            loss = max(0.3, loss * 0.85 + 0.05 * math.sin(step))
            logs.append(TrainLog(ep, step, round(loss, 4)))
    return logs


def main() -> None:
    mock = os.environ.get("SPARKTECH_MOCK", "1") == "1"
    logs = mock_train()
    out = Path(__file__).parent / "output" / "mock_train_log.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps([asdict(x) for x in logs], indent=2), encoding="utf-8")
    print(f"mock={mock} final_loss={logs[-1].loss} saved={out}")


if __name__ == "__main__":
    main()
''')
    w(f"day{d}/code/verify_day53.py", VERIFY_HEADER.format(day=d) + """
    from lora_math_demo import lora_delta_demo
    from lora_config_explainer import save_config
    from lora_mock_train import mock_train
    from pathlib import Path

    info = lora_delta_demo(r=8)
    if info["lora_params"] >= info["full_params"]:
        fail("lora should reduce params")
    ok("lora_math_demo")

    cfg_path = Path(__file__).parent / "configs" / "lora_sparktech.json"
    save_config(cfg_path)
    if not cfg_path.is_file():
        fail("config not saved")
    ok("lora_config")

    logs = mock_train(epochs=2, steps_per_epoch=3)
    if logs[-1].loss >= logs[0].loss:
        fail("loss should decrease in mock")
    ok("lora_mock_train")

    print("=== ALL PASSED ===")


if __name__ == "__main__":
    main()
""")
    w(f"day{d}/run.sh", RUN_SH.format(day=d))


def gen_day54() -> None:
    d = 54
    w(f"day{d}/README.md", day_readme(
        d, "LLaMA-Factory · 配置化微调实战",
        [
            ("09:00–10:30", "LLaMA-Factory 目录结构", "`llamafactory_configs/`"),
            ("10:30–12:00", "dataset_info 注册", "`dataset_info.json`"),
            ("14:00–16:00", "Mock Trainer", "`mock_llamafactory_train.py`"),
            ("16:00–17:00", "真机命令备忘", "`04_课堂讲义.md`"),
        ],
        "day53", "day55",
    ))
    bodies = {
        "01_业务背景": ("训练跑通", "张工：「有 GPU 的同学按 YAML 真训；无 GPU 用 mock 走通流水线。」"),
        "02_需求文档": ("训练 PRD", "产出 adapter 目录结构；训练日志含 loss/lr/step。"),
        "03_架构与设计": ("LLaMA-Factory 集成", "```text\ndata/sparktech_cs -> dataset_info -> YAML -> llamafactory-cli train```"),
        "04_课堂讲义": ("LLaMA-Factory", "## 安装\n`pip install llamafactory`\n\n## 命令\n`llamafactory-cli train configs/sparktech_qwen_lora.yaml`\n\n## Mock\n`python3 mock_llamafactory_train.py`"),
        "05_流程图与示意图": ("训练管线", "```mermaid\nflowchart LR\n  J[jsonl] --> LF[LLaMA-Factory]\n  LF --> A[adapter/]\n```"),
        "06_课后作业": ("", "修改 YAML 中 `num_train_epochs` 为 2，观察 mock 日志。"),
        "07_作业参考答案": ("", "epoch 增加 loss 更低但过拟合风险升。"),
        "08_补充讲义_GPU真机备忘": ("GPU", "单卡 24GB 建议 QLoRA；多卡用 deepspeed zero2。"),
    }
    for fname, (title, body) in bodies.items():
        w(f"day{d}/{fname}.md", std_md(d, fname.split("_")[0], title, body))

    w(f"day{d}/code/llamafactory_configs/sparktech_qwen_lora.yaml", """\
### model
model_name_or_path: Qwen/Qwen2.5-7B-Instruct
trust_remote_code: true

### method
stage: sft
do_train: true
finetuning_type: lora
lora_rank: 8
lora_alpha: 16
lora_target: q_proj,v_proj

### dataset
dataset: sparktech_cs
template: qwen
cutoff_len: 1024

### output
output_dir: output/sparktech_lora
logging_steps: 10
save_steps: 100
num_train_epochs: 1
per_device_train_batch_size: 1
learning_rate: 1.0e-4

### 教学说明
# 有 GPU: llamafactory-cli train llamafactory_configs/sparktech_qwen_lora.yaml
# 无 GPU: python3 mock_llamafactory_train.py
""")
    w(f"day{d}/code/dataset_info.json", json.dumps({
        "sparktech_cs": {
            "file_name": "../day52/code/data/train.jsonl",
            "formatting": "alpaca",
            "columns": {"prompt": "instruction", "query": "input", "response": "output"},
        }
    }, ensure_ascii=False, indent=2))
    w(f"day{d}/code/mock_llamafactory_train.py", '''# -*- coding: utf-8 -*-
"""Day 54 · 模拟 LLaMA-Factory 训练输出目录结构。"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from day52_import import ensure_day52_data  # noqa — defined below inline


OUTPUT = Path(__file__).parent / "output" / "sparktech_lora"


def run_mock_train() -> Path:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    adapter = {
        "peft_type": "LORA",
        "r": 8,
        "lora_alpha": 16,
        "target_modules": ["q_proj", "v_proj"],
    }
    (OUTPUT / "adapter_config.json").write_text(json.dumps(adapter, indent=2), encoding="utf-8")
    (OUTPUT / "adapter_model.bin").write_bytes(b"MOCK_LORA_WEIGHTS")
    (OUTPUT / "trainer_log.jsonl").write_text(
        '{"loss": 1.2, "step": 10}\\n{"loss": 0.8, "step": 20}\\n',
        encoding="utf-8",
    )
    return OUTPUT


if __name__ == "__main__":
    p = run_mock_train()
    print(f"mock adapter at {p}")
''')
    # fix import - use inline helper instead
    w(f"day{d}/code/mock_llamafactory_train.py", '''# -*- coding: utf-8 -*-
"""Day 54 · 模拟 LLaMA-Factory 训练输出目录结构。"""

from __future__ import annotations

import json
from pathlib import Path


OUTPUT = Path(__file__).parent / "output" / "sparktech_lora"


def run_mock_train() -> Path:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    adapter = {
        "peft_type": "LORA",
        "r": 8,
        "lora_alpha": 16,
        "target_modules": ["q_proj", "v_proj"],
        "base_model": "Qwen/Qwen2.5-7B-Instruct",
    }
    (OUTPUT / "adapter_config.json").write_text(json.dumps(adapter, indent=2), encoding="utf-8")
    (OUTPUT / "adapter_model.bin").write_bytes(b"MOCK_LORA_WEIGHTS_SPARKTECH")
    (OUTPUT / "trainer_log.jsonl").write_text(
        '{"loss": 1.2, "step": 10}\\n{"loss": 0.8, "step": 20}\\n',
        encoding="utf-8",
    )
    readme = OUTPUT / "README.txt"
    readme.write_text(
        "Mock adapter for teaching. Replace with real LLaMA-Factory output on GPU.\\n",
        encoding="utf-8",
    )
    return OUTPUT


if __name__ == "__main__":
    p = run_mock_train()
    print(f"mock adapter at {p}")
''')
    w(f"day{d}/code/verify_day54.py", VERIFY_HEADER.format(day=d) + """
    from pathlib import Path
    from mock_llamafactory_train import run_mock_train
    import json

    yaml = Path(__file__).parent / "llamafactory_configs" / "sparktech_qwen_lora.yaml"
    if "lora_rank" not in yaml.read_text(encoding="utf-8"):
        fail("yaml missing lora_rank")
    ok("llamafactory yaml")

    out = run_mock_train()
    cfg = out / "adapter_config.json"
    if not cfg.is_file():
        fail("adapter_config missing")
    data = json.loads(cfg.read_text(encoding="utf-8"))
    if data.get("peft_type") != "LORA":
        fail("not LORA")
    ok("mock adapter output")

    print("=== ALL PASSED ===")


if __name__ == "__main__":
    main()
""")
    w(f"day{d}/run.sh", RUN_SH.format(day=d))


def gen_day55() -> None:
    d = 55
    w(f"day{d}/README.md", day_readme(
        d, "微调评估 · 离线指标与 A/B 对比",
        [
            ("09:00–10:30", "黄金集设计", "`data/golden_eval.jsonl`"),
            ("10:30–12:00", "自动指标", "`evaluate_responses.py`"),
            ("14:00–16:00", "LLM-as-Judge mock", "`llm_judge_mock.py`"),
            ("16:00–17:00", "A/B 报告", "`ab_test_runner.py`"),
        ],
        "day54", "day56",
    ))
    bodies = {
        "01_业务背景": ("上线门禁", "微调模型不得直接上生产；黄金集得分须超 base 5% 且护栏全过。"),
        "02_需求文档": ("评估 PRD", "指标：tone_score, factuality, length；输出 `reports/ab_summary.json`。"),
        "03_架构与设计": ("评估链路", "golden -> base model -> finetuned -> judge -> report"),
        "04_课堂讲义": ("评估方法", "## 自动\nBLEU/ROUGE 参考\n\n## Judge\nRubric 打分\n\n## A/B\n同一 prompt 对比"),
        "05_流程图与示意图": ("评估流", "```mermaid\nflowchart LR\n  G[Golden] --> E[Eval]\n  E --> R[Report]\n```"),
        "06_课后作业": ("", "新增 5 条黄金集；调 judge rubric 权重。"),
        "07_作业参考答案": ("", "tone 权重 0.4，factuality 0.4，brevity 0.2。"),
        "08_补充讲义_评估陷阱": ("陷阱", "训练集泄漏到黄金集会导致虚高。"),
    }
    for fname, (title, body) in bodies.items():
        w(f"day{d}/{fname}.md", std_md(d, fname.split("_")[0], title, body))

    golden = [
        {"id": "g1", "prompt": "客户催退款", "reference": "已加急，1-3工作日到账"},
        {"id": "g2", "prompt": "投诉慢", "reference": "抱歉，30分钟内回电"},
    ]
    w(f"day{d}/code/data/golden_eval.jsonl", "\n".join(json.dumps(g, ensure_ascii=False) for g in golden) + "\n")
    w(f"day{d}/code/evaluate_responses.py", '''# -*- coding: utf-8 -*-
"""Day 55 · 简单自动评估（关键词覆盖）。"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class EvalScore:
    id: str
    keyword_hit: float
    length_ok: bool


def keyword_score(response: str, reference: str) -> float:
    keys = set(re.findall(r"[\\u4e00-\\u9fff]{2,}", reference))
    if not keys:
        return 0.0
    hit = sum(1 for k in keys if k in response)
    return hit / len(keys)


def eval_pair(item_id: str, response: str, reference: str) -> EvalScore:
    return EvalScore(item_id, keyword_score(response, reference), 20 <= len(response) <= 300)


def load_golden(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def main() -> None:
    golden = load_golden(Path(__file__).parent / "data" / "golden_eval.jsonl")
    for g in golden:
        base = "您好，我们会尽快处理。"
        tuned = g["reference"] + "，感谢理解。"
        s = eval_pair(g["id"], tuned, g["reference"])
        print(g["id"], s)
''')
    w(f"day{d}/code/llm_judge_mock.py", '''# -*- coding: utf-8 -*-
"""Day 55 · Mock LLM-as-Judge。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class JudgeResult:
    tone: float
    factuality: float
    overall: float


def judge(response: str, reference: str) -> JudgeResult:
    tone = 0.9 if "抱歉" in response or "您好" in response else 0.6
    fact = 0.85 if any(w in response for w in reference.split()[:2]) or reference[:2] in response else 0.5
    overall = 0.4 * tone + 0.4 * fact + 0.2 * min(1.0, len(response) / 80)
    return JudgeResult(tone, fact, round(overall, 3))


if __name__ == "__main__":
    r = judge("您好，非常抱歉，已加急处理。", "已加急，1-3工作日到账")
    print(r)
''')
    w(f"day{d}/code/ab_test_runner.py", '''# -*- coding: utf-8 -*-
"""Day 55 · Base vs Finetuned A/B 报告。"""

from __future__ import annotations

import json
from pathlib import Path

from evaluate_responses import load_golden, eval_pair
from llm_judge_mock import judge


def run_ab() -> dict:
    golden_path = Path(__file__).parent / "data" / "golden_eval.jsonl"
    rows = load_golden(golden_path)
    base_scores, tuned_scores = [], []
    for g in rows:
        base_resp = "好的，我们会处理您的问题。"
        tuned_resp = g["reference"]
        base_scores.append(judge(base_resp, g["reference"]).overall)
        tuned_scores.append(judge(tuned_resp, g["reference"]).overall)
    report = {
        "n": len(rows),
        "base_avg": round(sum(base_scores) / len(base_scores), 3),
        "tuned_avg": round(sum(tuned_scores) / len(tuned_scores), 3),
        "lift": round(sum(tuned_scores) / len(tuned_scores) - sum(base_scores) / len(base_scores), 3),
    }
    out = Path(__file__).parent / "reports" / "ab_summary.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    print(run_ab())
''')
    w(f"day{d}/code/verify_day55.py", VERIFY_HEADER.format(day=d) + """
    from ab_test_runner import run_ab

    report = run_ab()
    if report["n"] < 1:
        fail("no golden samples")
    if report["tuned_avg"] <= report["base_avg"]:
        fail("tuned should beat base in mock")
    ok("ab_test_runner")

    print("=== ALL PASSED ===")


if __name__ == "__main__":
    main()
""")
    w(f"day{d}/run.sh", RUN_SH.format(day=d))


def gen_day56() -> None:
    d = 56
    w(f"day{d}/README.md", day_readme(
        d, "vLLM 推理服务 · OpenAI 兼容 API",
        [
            ("09:00–10:30", "vLLM 架构", "`04_课堂讲义.md`"),
            ("10:30–12:00", "Mock OpenAI Server", "`mock_vllm_server.py`"),
            ("14:00–16:00", "客户端与压测", "`openai_client.py`"),
            ("16:00–17:00", "延迟 benchmark", "`benchmark_latency.py`"),
        ],
        "day55", "day57",
    ))
    bodies = {
        "01_业务背景": ("推理上线", "训练完成；今日把 adapter 挂到 vLLM，提供 `/v1/chat/completions`。"),
        "02_需求文档": ("推理 PRD", "OpenAI 兼容；支持 stream；P99 < 2s（mock 测逻辑）。"),
        "03_架构与设计": ("vLLM 部署", "Client -> vLLM -> GPU KV cache；教学用 mock server。"),
        "04_课堂讲义": ("vLLM", "## 启动\n`python -m vllm.entrypoints.openai.api_server`\n\n## 参数\n--tensor-parallel-size\n\n## Mock\n`uvicorn mock_vllm_server:app`"),
        "05_流程图与示意图": ("推理", "```mermaid\nflowchart LR\n  C[Client] --> V[vLLM]\n  V --> M[Model+LoRA]\n```"),
        "06_课后作业": ("", "用 curl 调 mock `/v1/chat/completions`。"),
        "07_作业参考答案": ("", "见 `openai_client.py` 示例。"),
        "08_补充讲义_vLLM参数表": ("参数", "| 参数 | 含义 |\n| max_model_len | 上下文 |"),
    }
    for fname, (title, body) in bodies.items():
        w(f"day{d}/{fname}.md", std_md(d, fname.split("_")[0], title, body))

    w(f"day{d}/code/mock_vllm_server.py", '''# -*- coding: utf-8 -*-
"""Day 56 · Mock vLLM OpenAI 兼容服务。"""

from __future__ import annotations

import os
import time
import uuid
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="SparkTech Mock vLLM", version="0.1.0")


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str = "sparktech-qwen-lora"
    messages: list[ChatMessage]
    stream: bool = False
    temperature: float = 0.7


class ChatResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    model: str
    choices: list[dict[str, Any]]


MOCK_REPLIES = {
    "退款": "您好，退款一般3-5个工作日到账，已为您加急。",
    "投诉": "非常抱歉给您带来不便，专员将在30分钟内联系您。",
}


def generate_reply(messages: list[ChatMessage]) -> str:
    user = ""
    for m in reversed(messages):
        if m.role == "user":
            user = m.content
            break
    for k, v in MOCK_REPLIES.items():
        if k in user:
            return v
    return "您好，我是星火智服微调客服模型，请问有什么可以帮您？"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "engine": "mock-vllm"}


@app.post("/v1/chat/completions")
def chat(req: ChatRequest) -> ChatResponse:
    if os.environ.get("SPARKTECH_MOCK_FAIL"):
        raise RuntimeError("simulated failure")
    time.sleep(0.05)
    text = generate_reply(req.messages)
    return ChatResponse(
        id=f"chatcmpl-{uuid.uuid4().hex[:12]}",
        model=req.model,
        choices=[{"index": 0, "message": {"role": "assistant", "content": text}, "finish_reason": "stop"}],
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8100)
''')
    w(f"day{d}/code/openai_client.py", '''# -*- coding: utf-8 -*-
"""Day 56 · 调用 Mock vLLM（OpenAI 格式）。"""

from __future__ import annotations

import json
import os
import urllib.request


def chat_completion(prompt: str, *, base_url: str | None = None) -> str:
    base = base_url or os.environ.get("VLLM_BASE_URL", "http://127.0.0.1:8100")
    payload = {
        "model": "sparktech-qwen-lora",
        "messages": [{"role": "user", "content": prompt}],
    }
    req = urllib.request.Request(
        f"{base}/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"]


def local_mock_chat(prompt: str) -> str:
    """无 server 时的离线 fallback。"""
    from mock_vllm_server import generate_reply, ChatMessage
    return generate_reply([ChatMessage(role="user", content=prompt)])


if __name__ == "__main__":
    print(local_mock_chat("我要退款"))
''')
    w(f"day{d}/code/benchmark_latency.py", '''# -*- coding: utf-8 -*-
"""Day 56 · 延迟 benchmark（本地函数级）。"""

from __future__ import annotations

import statistics
import time

from openai_client import local_mock_chat


def bench(n: int = 20) -> dict:
    latencies = []
    for i in range(n):
        t0 = time.perf_counter()
        local_mock_chat(f"测试退款{i}")
        latencies.append((time.perf_counter() - t0) * 1000)
    return {
        "n": n,
        "p50_ms": round(statistics.median(latencies), 2),
        "p95_ms": round(sorted(latencies)[int(n * 0.95) - 1], 2),
    }


if __name__ == "__main__":
    print(bench())
''')
    w(f"day{d}/code/requirements.txt", "fastapi>=0.110\nuvicorn>=0.27\npydantic>=2.0\n")
    w(f"day{d}/code/verify_day56.py", VERIFY_HEADER.format(day=d) + """
    from mock_vllm_server import generate_reply, ChatMessage
    from openai_client import local_mock_chat
    from benchmark_latency import bench

    r = generate_reply([ChatMessage(role="user", content="退款怎么办")])
    if "退款" not in r:
        fail("mock reply missing keyword")
    ok("mock_vllm_server")

    r2 = local_mock_chat("投诉太慢")
    if "抱歉" not in r2:
        fail("local mock complaint")
    ok("openai_client")

    stats = bench(n=10)
    if stats["p95_ms"] > 5000:
        fail("latency too high")
    ok("benchmark_latency")

    print("=== ALL PASSED ===")


if __name__ == "__main__":
    main()
""")
    w(f"day{d}/run.sh", RUN_SH.format(day=d))


def gen_day57() -> None:
    d = 57
    w(f"day{d}/README.md", f"""# Day {d} · Docker 部署 · 阶段五收官（RAG + 微调推理联调）

> **旁白**  
> {BIZ_INTRO.strip()}  
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
""")
    bodies = {
        "01_业务背景": ("上线评审", "运维要求：镜像 < 2GB、健康检查、.env 外置、日志 stdout。"),
        "02_需求文档": ("部署 PRD", "`/health` 200；`/api/chat` 路由到 vLLM；compose 三服务。"),
        "03_架构与设计": ("Compose 拓扑", "api-gateway:8020, mock-vllm:8100, 可选 redis"),
        "04_课堂讲义": ("Docker 部署", "## 多阶段构建\n减小镜像\n\n## compose\ndepends_on + healthcheck\n\n## 环境变量\nVLLM_BASE_URL"),
        "05_流程图与示意图": ("部署图", "```mermaid\nflowchart TB\n  U[User] --> GW[Gateway:8020]\n  GW --> VLLM[mock-vllm:8100]\n```"),
        "06_课后作业": ("", "为 gateway 增加 `/metrics` 占位端点。"),
        "07_作业参考答案": ("", "返回 `{{\"requests\": 0}}` 即可。"),
        "08_补充讲义_生产上线清单": ("清单", "镜像扫描、资源 limit、滚动更新、备份 adapter。"),
    }
    for fname, (title, body) in bodies.items():
        w(f"day{d}/{fname}.md", std_md(d, fname.split("_")[0], title, body))

    w(f"day{d}/code/deploy_stack/docker-compose.yml", """\
services:
  mock-vllm:
    build:
      context: ..
      dockerfile: deploy_stack/Dockerfile.vllm
    ports:
      - "8100:8100"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8100/health"]
      interval: 10s
      timeout: 3s
      retries: 3

  api-gateway:
    build:
      context: ..
      dockerfile: deploy_stack/Dockerfile.api
    ports:
      - "8020:8020"
    environment:
      VLLM_BASE_URL: http://mock-vllm:8100
      SPARKTECH_MOCK: "1"
    depends_on:
      mock-vllm:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8020/health"]
      interval: 10s
      timeout: 3s
      retries: 3
""")
    w(f"day{d}/code/deploy_stack/Dockerfile.vllm", """\
FROM python:3.11-slim
WORKDIR /app
COPY requirements-deploy.txt /app/
RUN pip install --no-cache-dir -r requirements-deploy.txt
COPY deploy_stack/mock_vllm_app.py /app/mock_vllm_app.py
EXPOSE 8100
CMD ["uvicorn", "mock_vllm_app:app", "--host", "0.0.0.0", "--port", "8100"]
""")
    w(f"day{d}/code/deploy_stack/Dockerfile.api", """\
FROM python:3.11-slim
WORKDIR /app
COPY requirements-deploy.txt /app/
RUN pip install --no-cache-dir -r requirements-deploy.txt
COPY deploy_stack/api_gateway /app/api_gateway
ENV PYTHONPATH=/app
EXPOSE 8020
CMD ["uvicorn", "api_gateway.main:app", "--host", "0.0.0.0", "--port", "8020"]
""")
    w(f"day{d}/code/requirements-deploy.txt", "fastapi>=0.110\nuvicorn>=0.27\npydantic>=2.0\nhttpx>=0.27\n")
    w(f"day{d}/code/deploy_stack/mock_vllm_app.py", '''# -*- coding: utf-8 -*-
"""Docker 用 Mock vLLM — 精简版。"""

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class ChatRequest(BaseModel):
    model: str = "sparktech-qwen-lora"
    messages: list[dict]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/v1/chat/completions")
def chat(req: ChatRequest):
    user = req.messages[-1]["content"] if req.messages else ""
    text = "您好，Docker 内 mock vLLM 已收到：" + user[:50]
    return {
        "id": "mock",
        "choices": [{"message": {"role": "assistant", "content": text}}],
    }
''')
    w(f"day{d}/code/deploy_stack/api_gateway/main.py", '''# -*- coding: utf-8 -*-
"""Day 57 · API 网关 — 路由到 vLLM。"""

from __future__ import annotations

import os
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="SparkTech Deploy Gateway")
VLLM_BASE = os.environ.get("VLLM_BASE_URL", "http://127.0.0.1:8100")


class ChatRequest(BaseModel):
    message: str
    route: str = "finetuned"  # finetuned | rag | fallback


class ChatResponse(BaseModel):
    reply: str
    route: str
    backend: str


@app.get("/health")
def health():
    return {"status": "ok", "vllm": VLLM_BASE}


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if req.route == "rag":
        return ChatResponse(
            reply="[RAG] 请查阅知识库政策文档（教学占位）",
            route="rag",
            backend="project2-placeholder",
        )
    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.post(
                f"{VLLM_BASE}/v1/chat/completions",
                json={
                    "model": "sparktech-qwen-lora",
                    "messages": [{"role": "user", "content": req.message}],
                },
            )
            r.raise_for_status()
            data = r.json()
            text = data["choices"][0]["message"]["content"]
    except Exception as e:
        if os.environ.get("SPARKTECH_MOCK") == "1":
            text = f"[mock-gateway] {req.message}"
        else:
            raise HTTPException(502, str(e)) from e
    return ChatResponse(reply=text, route=req.route, backend="vllm")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8020)
''')
    w(f"day{d}/code/verify_day57.py", VERIFY_HEADER.format(day=d) + """
    import sys
    from pathlib import Path

    # 复用 day56 mock
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "day56" / "code"))
    from deploy_stack.api_gateway.main import app as gateway_app  # noqa — local import below

    sys.path.insert(0, str(Path(__file__).parent / "deploy_stack"))
    sys.path.insert(0, str(Path(__file__).parent))
    from deploy_stack.api_gateway.main import chat, health
    from deploy_stack.mock_vllm_app import chat as vllm_chat, health as vllm_health

    h = health()
    if h.get("status") != "ok":
        fail("gateway health")
    ok("gateway health")

    vh = vllm_health()
    if vh.get("status") != "ok":
        fail("vllm health")
    ok("mock vllm health")

    # offline gateway mock path
    import os
    os.environ["SPARKTECH_MOCK"] = "1"
    from deploy_stack.api_gateway import main as gw

    class Req:
        message = "退款"
        route = "finetuned"

    # use FastAPI TestClient
    from fastapi.testclient import TestClient
    client = TestClient(gw.app)
    r = client.post("/api/chat", json={"message": "退款", "route": "finetuned"})
    if r.status_code != 200:
        fail(f"chat status {r.status_code}")
    body = r.json()
    if "reply" not in body:
        fail("no reply")
    ok("gateway /api/chat")

    r2 = client.post("/api/chat", json={"message": "政策", "route": "rag"})
    if "RAG" not in r2.json().get("reply", ""):
        fail("rag route")
    ok("rag route")

    compose = Path(__file__).parent / "deploy_stack" / "docker-compose.yml"
    if not compose.is_file():
        fail("docker-compose missing")
    ok("docker-compose.yml")

    print("=== ALL PASSED ===")


if __name__ == "__main__":
    main()
""")
    w(f"day{d}/run.sh", """#!/bin/bash
set -e
cd "$(dirname "$0")/code"
export SPARKTECH_MOCK=1
python3 verify_day57.py
echo ""
echo "可选: cd deploy_stack && docker compose up --build"
""")


def gen_curriculum() -> None:
    w("curriculum/05_阶段五_微调与部署_Day51-57.md", """\
# 阶段五学习路径索引 · Day 51–57（微调与部署）

> Phase4：**垂直客服 LoRA + vLLM + Docker** 上线，与 Project2 RAG 并存。

---

## 一、阶段目标

| 产出 | 说明 |
|------|------|
| 数据集 | `day52/code/data/train.jsonl` |
| LoRA 配置 | `day53/code/configs/lora_sparktech.json` |
| 训练产物 | `day54/code/output/sparktech_lora/`（mock 或真机） |
| 评估报告 | `day55/code/reports/ab_summary.json` |
| 推理服务 | `day56` Mock vLLM `:8100` |
| 部署栈 | `day57` Gateway `:8020` + Compose |

---

## 二、每日导航

| 天 | 目录 | 关键词 | 验收 |
|----|------|--------|------|
| 51 | day51/ | 微调选型 | `verify_day51.py` |
| 52 | day52/ | 数据集工程 | `verify_day52.py` |
| 53 | day53/ | LoRA 原理 | `verify_day53.py` |
| 54 | day54/ | LLaMA-Factory | `verify_day54.py` |
| 55 | day55/ | 离线评估 | `verify_day55.py` |
| 56 | day56/ | vLLM 推理 | `verify_day56.py` |
| 57 | day57/ | Docker 部署 | `verify_day57.py` |

---

## 三、技术演进链

```mermaid
flowchart LR
    P2[Day36 RAG] --> D51[Day51 选型]
    D51 --> D52[数据集]
    D52 --> D53[LoRA]
    D53 --> D54[LLaMA-Factory]
    D54 --> D55[评估]
    D55 --> D56[vLLM]
    D56 --> D57[Docker]
    D57 --> D58[毕业设计]
```

---

## 四、环境变量

| 变量 | 用途 |
|------|------|
| `SPARKTECH_MOCK=1` | 无 GPU/API 时全链路 mock |
| `VLLM_BASE_URL` | 推理服务地址 |
| `CUDA_VISIBLE_DEVICES` | 真机训练 |

---

## 五、端口约定

| 服务 | 端口 |
|------|------|
| Project2 RAG | 8000 / 8080 |
| Project3 Agent | 8010 / 8088 |
| Mock vLLM | 8100 |
| Deploy Gateway | 8020 |

---

*索引 · 2026-07-06*
""")


def main() -> None:
    print("Generating Day 51-57...")
    gen_day51()
    gen_day52()
    gen_day53()
    gen_day54()
    gen_day55()
    gen_day56()
    gen_day57()
    gen_curriculum()
    for i in range(51, 58):
        run = ROOT / f"day{i}" / "run.sh"
        if run.exists():
            run.chmod(0o755)
    print("Done.")


if __name__ == "__main__":
    main()
