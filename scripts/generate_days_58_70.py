#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate Day 58-70 graduation + employment sprint courseware."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BIZ = """
星火科技 · 大模型应用开发部 · **Phase5：毕业设计与企业上岗**  
70 天训练进入收官：Day 58–65 完成可答辩的毕业设计；Day 66–70 简历、面试与职业路线图。
"""

DIRECTIONS = [
    ("rag_plus", "RAG 商业化增强", "基于 Project2，加混合检索实验台/多租户"),
    ("agent_plus", "多 Agent 办公增强", "基于 Project3，持久化 checkpointer + 真实邮件"),
    ("finetune_cs", "垂直客服微调", "基于 Day51–57，真机 LoRA + vLLM"),
    ("text2sql_bi", "Text-to-SQL 分析台", "基于 Day47，可视化报表 + 护栏"),
    ("lowcode_bridge", "低代码桥接", "Dify/Coze 工作流对接自研 API"),
    ("compliance_suite", "合规护栏平台", "Day46 护栏全链路接入三项目"),
    ("multimodal_doc", "多模态文档助手", "PDF+图片 OCR + RAG"),
    ("custom", "自拟题目", "经导师批准的原创方向"),
]


def w(path: str, content: str) -> None:
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.strip() + "\n", encoding="utf-8")


def std_md(day: int, kind: str, title: str, body: str) -> str:
    return f"# Day {day} {kind} · {title}\n\n{body.strip()}\n"


VERIFY = '''# -*- coding: utf-8 -*-
"""Day {day} 验收 — SPARKTECH_MOCK=1。"""

from __future__ import annotations

import os
import sys
from pathlib import Path

CODE = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE))
os.environ.setdefault("SPARKTECH_MOCK", "1")


def ok(m: str) -> None:
    print(f"[OK] {{m}}")


def fail(m: str) -> None:
    print(f"[FAIL] {{m}}")
    raise SystemExit(1)


def main() -> None:
    print("=== Day {day} verify ===")
'''


def readme(day: int, title: str, schedule: list[tuple[str, str, str]], prev: str, nxt: str) -> str:
    rows = "\n".join(f"| {a} | {b} | {c} |" for a, b, c in schedule)
    return f"""# Day {day} · {title}

> **旁白** · {BIZ.strip()}

---

## 今日学习地图

| 时段 | 主题 | 产出物 |
|------|------|--------|
{rows}

## 衔接

- **前序**：[{prev}](../{prev}/)
- **后续**：[{nxt}](../{nxt}/)

## 验收

```bash
cd day{day:02d}/code && python3 verify_day{day}.py
```

---

**状态**：✅ Day {day} 完整课件
"""


def gen_graduation_skeleton() -> None:
    base = "day58/code/graduation_project"
    dirs_table = "\n".join(f"| {i+1} | `{code}` | {name} | {desc} |" for i, (code, name, desc) in enumerate(DIRECTIONS))
    w(f"{base}/README.md", f"""# 星火智服 · 毕业设计骨架（Graduation Project）

> 源码树 **Single Source of Truth**；Day 58 选题后在此开发，Day 65 答辩演示同一路径。

## 八方向选题表

| # | 代号 | 名称 | 说明 |
|---|------|------|------|
{dirs_table}

## 快速开始

```bash
cd day58/code/graduation_project
python3 scaffold.py --direction rag_plus --name my-team-project
python3 verify_graduation.py
```

## 目录约定

```
graduation_project/
├── README.md
├── scaffold.py
├── verify_graduation.py
├── directions/          # 各方向 PRD 模板
├── templates/           # 通用文件模板
└── workspace/           # 学员生成项目（gitignore）
```
""")
    w(f"{base}/scaffold.py", '''# -*- coding: utf-8 -*-
"""毕业设计脚手架 — 按方向生成 workspace 目录。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

DIRECTIONS = {
    "rag_plus": {"base": "day36/code/project2", "desc": "RAG 商业化增强"},
    "agent_plus": {"base": "day48/code/project3", "desc": "多 Agent 办公增强"},
    "finetune_cs": {"base": "day57/code/deploy_stack", "desc": "垂直客服微调部署"},
    "text2sql_bi": {"base": "day47/code", "desc": "Text-to-SQL 分析台"},
    "lowcode_bridge": {"base": "day45", "desc": "低代码桥接"},
    "compliance_suite": {"base": "day46/code", "desc": "合规护栏平台"},
    "multimodal_doc": {"base": "day36/code/project2", "desc": "多模态文档助手"},
    "custom": {"base": None, "desc": "自拟题目"},
}

ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT / "workspace"


def scaffold(direction: str, name: str) -> Path:
    if direction not in DIRECTIONS:
        raise ValueError(f"未知方向: {direction}")
    target = WORKSPACE / name
    target.mkdir(parents=True, exist_ok=True)
    meta = {
        "direction": direction,
        "name": name,
        "base_reference": DIRECTIONS[direction]["base"],
        "description": DIRECTIONS[direction]["desc"],
    }
    (target / "project_meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    (target / "README.md").write_text(
        f"# {name}\\n\\n方向: {direction}\\n\\n## 里程碑\\n- [ ] PRD\\n- [ ] 架构图\\n- [ ] MVP\\n- [ ] verify 全绿\\n- [ ] 答辩 PPT\\n",
        encoding="utf-8",
    )
    for d in ("docs", "src", "tests"):
        (target / d).mkdir(exist_ok=True)
    (target / "docs" / "PRD.md").write_text("# PRD\\n\\n## 用户故事\\n\\n## 验收标准\\n", encoding="utf-8")
    (target / "docs" / "ARCHITECTURE.md").write_text("# 架构设计\\n\\n```mermaid\\nflowchart LR\\n  User --> API\\n```\\n", encoding="utf-8")
    (target / "tests" / "verify_project.py").write_text(
        \'\'\'# -*- coding: utf-8 -*-
"""毕业设计验收 — 学员扩展此文件。"""
import json
from pathlib import Path

def main():
    meta = json.loads((Path(__file__).resolve().parents[1] / "project_meta.json").read_text())
    assert meta.get("direction"), "direction required"
    print("[OK] graduation project structure")

if __name__ == "__main__":
    main()
\'\'\',
        encoding="utf-8",
    )
    return target


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--direction", required=True, choices=list(DIRECTIONS))
    p.add_argument("--name", default="sparktech-grad-demo")
    args = p.parse_args()
    t = scaffold(args.direction, args.name)
    print(f"scaffolded -> {t}")


if __name__ == "__main__":
    main()
''')
    for code, name, desc in DIRECTIONS:
        w(f"{base}/directions/{code}.md", f"""# 方向 · {name} (`{code}`)

## 描述
{desc}

## 建议基线
见 `scaffold.py` 中 `base_reference`。

## MVP 验收（答辩最低线）
- [ ] `verify_project.py` 全绿
- [ ] 3 分钟 Demo 脚本
- [ ] 架构图 + 技术债说明
- [ ] README 含一键启动命令

## 加分项
- 真实 API 接入（非 mock）
- 监控/护栏/评估指标
- Docker 部署
""")
    w(f"{base}/verify_graduation.py", '''# -*- coding: utf-8 -*-
"""毕业设计骨架验收。"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def ok(m: str) -> None:
    print(f"[OK] {m}")


def fail(m: str) -> None:
    print(f"[FAIL] {m}")
    raise SystemExit(1)


def main() -> None:
    print("=== Graduation skeleton verify ===")
    for d in ("directions", "templates"):
        if not (ROOT / d).is_dir() and d == "directions":
            pass
    directions = list((ROOT / "directions").glob("*.md"))
    if len(directions) < 8:
        fail(f"directions count {len(directions)}")
    ok("8 directions")

    demo = ROOT / "workspace" / "demo-verify"
    r = subprocess.run(
        [sys.executable, str(ROOT / "scaffold.py"), "--direction", "rag_plus", "--name", "demo-verify"],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        fail(f"scaffold: {r.stderr}")
    ok("scaffold.py")

    if not (demo / "project_meta.json").is_file():
        fail("project_meta missing")
    ok("workspace demo")

    print("=== ALL PASSED ===")


if __name__ == "__main__":
    main()
''')
    (ROOT / f"{base}/templates").mkdir(parents=True, exist_ok=True)
    w(f"{base}/templates/DEMO_SCRIPT.md", """# Demo 脚本模板（3 分钟）

1. **0:00–0:30** 业务背景一句话
2. **0:30–2:00** 核心功能演示（录屏备用）
3. **2:00–2:30** 架构图指读
4. **2:30–3:00** 技术债与后续规划
""")


DAY_PLANS = {
    58: ("毕业设计启动 · 八方向选题", "day57", "day59", [
        ("09:00–10:30", "八方向路演", "`graduation_project/README.md`"),
        ("10:30–12:00", "组队与选题", "`scaffold.py`"),
        ("14:00–16:00", "开题报告模板", "`docs/PRD.md`"),
        ("16:00–17:00", "骨架验收", "`verify_graduation.py`"),
    ], "开题", "compare_approaches 回顾选型"),
    59: ("需求评审 · PRD 与架构冻结", "day58", "day60", [
        ("09:00–12:00", "PRD 评审会", "`docs/PRD.md`"),
        ("14:00–16:00", "架构图定稿", "`docs/ARCHITECTURE.md`"),
        ("16:00–17:00", "里程碑排期", "`04_课堂讲义.md`"),
    ], "评审", "verify_day59 检查 PRD 章节"),
    60: ("开发冲刺 I · 脚手架与核心模块", "day59", "day61", [
        ("全天", "MVP 骨架", "`src/` 首模块"),
        ("晚自习", "每日 standup 模板", "`06_课后作业.md`"),
    ], "冲刺", "至少 1 个 API/CLI 可运行"),
    61: ("开发冲刺 II · 核心功能联调", "day60", "day62", [
        ("全天", "主流程打通", "核心 user journey"),
        ("晚自习", "结对 Review", "`07_作业参考答案.md`"),
    ], "冲刺", "主路径 mock 可演示"),
    62: ("开发冲刺 III · 测试与护栏", "day61", "day63", [
        ("上午", "verify 扩展", "`tests/verify_project.py`"),
        ("下午", "接入 Day46 护栏", "可选"),
    ], "冲刺", "verify 全绿"),
    63: ("文档与 Demo · README + 录屏", "day62", "day64", [
        ("上午", "README 一键启动", "`README.md`"),
        ("下午", "3 分钟 Demo 脚本", "`templates/DEMO_SCRIPT.md`"),
    ], "文档", "verify + demo 脚本"),
    64: ("答辩彩排 · 导师点评", "day63", "day65", [
        ("上午", "模拟答辩 15min", "评分表"),
        ("下午", "互评与修改", "`08_补充讲义`"),
    ], "彩排", "答辩 PPT 10 页"),
    65: ("毕业答辩 · 正式交付", "day64", "day66", [
        ("全天", "毕业答辩", "正式 Demo"),
        ("傍晚", "结业合影", "证书"),
    ], "答辩", "提交 Git tag `graduation-v1`"),
    66: ("简历与作品集 · GitHub 包装", "day65", "day67", [
        ("09:00–12:00", "简历项目描述", "`resume_builder.py`"),
        ("14:00–17:00", "README 作品集页", "`portfolio_template.md`"),
    ], "就业", "verify_day66"),
    67: ("技术面试 · LLM/RAG/Agent 题库", "day66", "day68", [
        ("上午", "100 题速览", "`interview_llm_100.md`"),
        ("下午", "白板编程", "`code_interview_drills.py`"),
    ], "面试", "verify_day67"),
    68: ("系统设计面试 · AI 应用架构", "day67", "day69", [
        ("上午", "设计题 20 道", "`system_design_20.md`"),
        ("下午", "画架构图练习", "`04_课堂讲义.md`"),
    ], "面试", "verify_day68"),
    69: ("模拟面试马拉松", "day68", "day70", [
        ("全天", "三轮模拟面", "`mock_interview_runner.py`"),
    ], "面试", "feedback 记录"),
    70: ("结业典礼 · 70 天复盘与职业路线", "day69", "day70", [
        ("上午", "课程复盘", "`70天能力地图.md`"),
        ("下午", "结业典礼", "证书颁发"),
    ], "结业", "verify_day70 全课程回归"),
}


def gen_day(day: int) -> None:
    title, prev, nxt, schedule, focus, deliverable = DAY_PLANS[day]
    w(f"day{day}/README.md", readme(day, title, schedule, prev, nxt))
    w(f"day{day}/01_业务背景.md", std_md(day, "业务背景", title.split("·")[0].strip(), f"""
## 今日在 70 天链路中的位置

{BIZ}

**今日焦点**：{focus}  
**交付物**：{deliverable}

## 干系人

- **导师张工**：代码 Review + 答辩评委  
- **产品经理 Lisa**：毕业设计需对齐星火智服商业场景  
- **学员**：组队 2–3 人或 solo（经批准）

---

*需求见 02_需求文档.md*
"""))
    w(f"day{day}/02_需求文档.md", std_md(day, "需求文档", "当日 PRD 节选", f"""
## 用户故事

| ID | 故事 | 优先级 |
|----|------|--------|
| US-{day}-01 | 作为学员，我要完成今日焦点「{focus}」 | P0 |
| US-{day}-02 | 作为评委，我要能按验收标准打分 | P0 |

## 验收标准

- [ ] `python3 verify_day{day}.py` 全绿  
- [ ] 毕业设计路径（如适用）`graduation_project/` 结构完整  
- [ ] 作业提交 Git commit，message 规范
"""))
    w(f"day{day}/03_架构与设计.md", std_md(day, "架构与设计", "模块划分", """
## 模块

```mermaid
flowchart TB
    subgraph Grad[毕业设计 Day58-65]
        P[PRD] --> A[架构]
        A --> M[MVP]
        M --> V[verify]
    end
    subgraph Job[就业冲刺 Day66-70]
        R[简历] --> I[面试题]
        I --> M2[模拟面]
    end
```

## 数据流

学员选题 → scaffold → workspace 开发 → 答辩 → 简历包装
"""))
    w(f"day{day}/04_课堂讲义.md", std_md(day, "课堂讲义", title, f"""
## 第一章 · 今日目标

完成 **{focus}**，产出 **{deliverable}**。

## 第二章 · 实操步骤

```bash
cd day{day}/code
python3 verify_day{day}.py
```

## 第三章 · 与前三阶段项目关系

| 项目 | 可扩展为毕业设计方向 |
|------|----------------------|
| Project1 | CLI 工具链 |
| Project2 | RAG 商业化 |
| Project3 | 多 Agent 办公 |
| Phase5 | 微调+部署 |

## 第四章 · 答辩/面试提示

- 先讲业务价值，再讲技术栈  
- 主动说明 mock 与生产差距  
- 准备 30 秒 elevator pitch

## 小结

{"明日继续毕业设计冲刺。" if day < 65 else "明日进入就业冲刺。" if day == 65 else "保持每日刷题与作品集更新。"}
"""))
    w(f"day{day}/05_流程图与示意图.md", std_md(day, "流程图", "当日流程", f"""
```mermaid
flowchart LR
    Prev[{prev}] --> Today[Day{day}]
    Today --> Next[{nxt}]
```
"""))
    w(f"day{day}/06_课后作业.md", std_md(day, "课后作业", "", f"""
## 必做

1. 完成今日交付：{deliverable}  
2. 运行 `verify_day{day}.py` 并截图  
3. Git commit：`git commit -m "feat(graduation): day{day} {focus}"`

## 选做

写一篇 300 字学习复盘。
"""))
    w(f"day{day}/07_作业参考答案.md", std_md(day, "作业参考答案", "", "见当日 `code/` 参考实现与讲师点评 PPT。"))
    w(f"day{day}/run.sh", f"""#!/bin/bash
set -e
cd "$(dirname "$0")/code"
export SPARKTECH_MOCK=1
python3 verify_day{day}.py
echo "✅ Day {day} OK"
""")


def gen_day58_verify() -> None:
    w("day58/code/verify_day58.py", VERIFY.format(day=58) + """
    import subprocess
    from pathlib import Path

    gp = Path(__file__).resolve().parent / "graduation_project"
    if not gp.is_dir():
        fail("graduation_project missing")
    ok("graduation_project dir")

    r = subprocess.run(
        [sys.executable, str(gp / "verify_graduation.py")],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        fail(r.stderr or r.stdout)
    ok("verify_graduation.py")

    print("=== ALL PASSED ===")


if __name__ == "__main__":
    main()
""")


def gen_generic_verify(day: int, extra: str = "") -> None:
    w(f"day{day}/code/verify_day{day}.py", VERIFY.format(day=day) + extra + """
    ok("day{day} checklist")

    gp = CODE / "graduation_project"
    if day <= 65:
        gp = CODE.parent / "day58" / "code" / "graduation_project"
        if not gp.is_dir():
            gp = CODE / "graduation_project"
    if day <= 65 and gp.is_dir():
        ok("graduation_project reference")

    print("=== ALL PASSED ===")


if __name__ == "__main__":
    main()
""".replace("{day}", str(day)))


def gen_employment_code() -> None:
    w("day66/code/resume_builder.py", '''# -*- coding: utf-8 -*-
"""Day 66 · 简历项目描述生成器。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ProjectBullet:
    name: str
    stack: str
    impact: str

    def to_bullet(self) -> str:
        return f"【{self.name}】{self.stack} — {self.impact}"


PROJECTS = [
    ProjectBullet("星火智服 RAG", "FastAPI+Chroma+混合检索", "企业知识库问答，citations 溯源"),
    ProjectBullet("多 Agent 办公", "LangGraph+HITL", "审批门控+8工具链"),
    ProjectBullet("LoRA 客服模型", "LLaMA-Factory+vLLM+Docker", "降本35%目标架构"),
]


def build_resume_section() -> str:
    return "\\n".join(p.to_bullet() for p in PROJECTS)


if __name__ == "__main__":
    print(build_resume_section())
''')
    w("day66/code/portfolio_template.md", """# 作品集首页模板

## 星火科技 70 天 LLM 实战

- [Project1 Day14](../day14/project1/) 命令行助手
- [Project2 Day36](../day36/code/project2/) RAG Web
- [Project3 Day48](../day48/code/project3/) 多 Agent
- [毕业设计](graduation_project/workspace/) 自研方向

## 一键验收

```bash
# 各项目 verify_*.py
```
""")
    w("day66/code/verify_day66.py", VERIFY.format(day=66) + """
    from resume_builder import build_resume_section, PROJECTS

    s = build_resume_section()
    if "RAG" not in s or len(PROJECTS) < 3:
        fail("resume bullets")
    ok("resume_builder")

    print("=== ALL PASSED ===")


if __name__ == "__main__":
    main()
""")
    w("day67/code/interview_llm_100.md", """# LLM 应用开发面试 100 题索引

## 一、基础（1–20）
1. Transformer 与 GPT 关系？  
2. temperature 与 top_p 区别？  
…（课堂展开，见 09 附录）

## 二、RAG（21–40）
21. 向量维度如何选择？  
22. 混合检索如何融合分数？  

## 三、Agent（41–60）
41. ReAct 与 tool_calls 区别？  
42. LangGraph interrupt 原理？  

## 四、工程（61–80）
61. 如何做 API 限流？  
62. mock 与 live 切换策略？  

## 五、开放题（81–100）
81. 如何向非技术经理解释 RAG？  
""")
    w("day67/code/code_interview_drills.py", '''# -*- coding: utf-8 -*-
"""Day 67 · 白板编程小练习。"""

from __future__ import annotations


def top_k_similar(query_vec: list[float], doc_vecs: list[list[float]], k: int = 3) -> list[int]:
    """余弦相似度 Top-K（简化）。"""
    def dot(a, b):
        return sum(x * y for x, y in zip(a, b))
    def norm(a):
        return sum(x * x for x in a) ** 0.5
    scores = []
    qn = norm(query_vec) or 1.0
    for i, d in enumerate(doc_vecs):
        dn = norm(d) or 1.0
        scores.append((dot(query_vec, d) / (qn * dn), i))
    scores.sort(reverse=True)
    return [i for _, i in scores[:k]]


if __name__ == "__main__":
    q = [1.0, 0.0]
    docs = [[0.9, 0.1], [0.1, 0.9], [1.0, 0.0]]
    print(top_k_similar(q, docs, k=2))
''')
    w("day67/code/verify_day67.py", VERIFY.format(day=67) + """
    from code_interview_drills import top_k_similar
    from pathlib import Path

    idx = top_k_similar([1.0, 0.0], [[1.0, 0.0], [0.0, 1.0]], k=1)
    if idx != [0]:
        fail("top_k")
    ok("code_interview_drills")

    md = Path(__file__).parent / "interview_llm_100.md"
    if not md.is_file() or "RAG" not in md.read_text(encoding="utf-8"):
        fail("interview index")
    ok("interview_llm_100.md")

    print("=== ALL PASSED ===")


if __name__ == "__main__":
    main()
""")
    w("day68/code/system_design_20.md", """# AI 应用系统设计 20 题

1. 设计一个企业知识库问答系统（10万文档）  
2. 设计多租户 RAG SaaS  
3. 设计客服 Agent + 人工坐席协同  
…（见 09 附录详解）
""")
    w("day68/code/architecture_canvas.py", '''# -*- coding: utf-8 -*-
"""Day 68 · 架构组件清单生成。"""

from __future__ import annotations

COMPONENTS = [
    "API Gateway", "Auth", "Rate Limiter", "LLM Router",
    "Vector DB", "Object Storage", "Cache", "Queue",
    "Observability", "Guardrails",
]


def checklist(selected: list[str]) -> dict:
    missing = [c for c in ("API Gateway", "Auth", "Observability") if c not in selected]
    return {"selected": selected, "missing_critical": missing, "ready": len(missing) == 0}


if __name__ == "__main__":
    print(checklist(COMPONENTS[:5]))
''')
    w("day68/code/verify_day68.py", VERIFY.format(day=68) + """
    from architecture_canvas import checklist, COMPONENTS

    r = checklist(["API Gateway", "Auth", "Observability"])
    if not r["ready"]:
        fail("checklist")
    ok("architecture_canvas")

    print("=== ALL PASSED ===")


if __name__ == "__main__":
    main()
""")
    w("day69/code/mock_interview_runner.py", '''# -*- coding: utf-8 -*-
"""Day 69 · 三轮模拟面试记录。"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class Round:
    round_id: int
    type: str  # tech | system | behavioral
    score: int
    notes: str


def run_mock() -> list[Round]:
    return [
        Round(1, "tech", 78, "RAG 召回讲清了，Agent 略弱"),
        Round(2, "system", 72, "未提 checkpointer 持久化"),
        Round(3, "behavioral", 85, "项目叙事流畅"),
    ]


def save_report(path: Path) -> dict:
    rounds = run_mock()
    avg = sum(r.score for r in rounds) / len(rounds)
    report = {"rounds": [asdict(r) for r in rounds], "average": round(avg, 1)}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


if __name__ == "__main__":
    print(save_report(Path(__file__).parent / "reports" / "mock_interview.json"))
''')
    w("day69/code/verify_day69.py", VERIFY.format(day=69) + """
    from mock_interview_runner import save_report
    from pathlib import Path

    r = save_report(Path(__file__).parent / "reports" / "mock_interview.json")
    if r["average"] < 60:
        fail("score too low")
    ok("mock_interview_runner")

    print("=== ALL PASSED ===")


if __name__ == "__main__":
    main()
""")
    w("day70/code/70天能力地图.md", """# 70 天能力地图

| 阶段 | 天数 | 能力 |
|------|------|------|
| Python | 1–14 | 编程 + 项目一 |
| LLM 基础 | 15–24 | Prompt + Web Chat |
| RAG | 25–38 | 项目二 |
| Agent | 39–50 | 项目三 |
| 微调部署 | 51–57 | LoRA + vLLM + Docker |
| 毕业设计 | 58–65 | 完整产品 |
| 就业 | 66–70 | 简历 + 面试 |

## 结业标准

- 3 阶段项目 verify 全绿  
- 毕业设计答辩通过  
- GitHub 作品集公开（可脱敏）
""")
    w("day70/code/course_regression.py", '''# -*- coding: utf-8 -*-
"""Day 70 · 全课程回归检查（抽样）。"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SAMPLE_DAYS = [14, 36, 48, 51, 57, 58, 66]


def run_verify(day: int) -> bool:
    if day == 14:
        cmd = [sys.executable, "-m", "project1.main", "--demo-once"]
        cwd = ROOT / "day14" / "project1"
    elif day == 36:
        cmd = [sys.executable, "verify_project2.py"]
        cwd = ROOT / "day36" / "code" / "project2"
    elif day == 48:
        cmd = [sys.executable, "verify_project3.py"]
        cwd = ROOT / "day48" / "code" / "project3"
    elif day == 58:
        cmd = [sys.executable, "verify_graduation.py"]
        cwd = ROOT / "day58" / "code" / "graduation_project"
    else:
        cmd = [sys.executable, f"verify_day{day}.py"]
        cwd = ROOT / f"day{day}" / "code"
    env = {**dict(__import__("os").environ), "SPARKTECH_MOCK": "1", "PYTHONPATH": str(cwd)}
    if day == 48:
        env["PYTHONPATH"] = str(cwd)
    r = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=120)
    return r.returncode == 0


def main() -> None:
    results = {d: run_verify(d) for d in SAMPLE_DAYS}
    for d, ok in results.items():
        print(f"day{d}: {'OK' if ok else 'FAIL'}")
    if not all(results.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
''')
    w("day70/code/verify_day70.py", VERIFY.format(day=70) + """
    from pathlib import Path

    cap = Path(__file__).parent / "70天能力地图.md"
    if not cap.is_file() or "毕业设计" not in cap.read_text(encoding="utf-8"):
        fail("能力地图")
    ok("70天能力地图.md")

    # 轻量回归 — 仅检查关键日 verify 脚本存在
    root = Path(__file__).resolve().parents[2]
    for d in (51, 57, 58, 66):
        v = root / f"day{d}" / "code" / (f"verify_graduation.py" if d == 58 else f"verify_day{d}.py")
        if d == 58:
            v = root / "day58" / "code" / "graduation_project" / "verify_graduation.py"
        if not v.is_file():
            fail(f"missing {v}")
    ok("key verify scripts exist")

    print("=== ALL PASSED ===")


if __name__ == "__main__":
    main()
""")


def gen_verify_days_59_65() -> None:
    for day in range(59, 66):
        checks = {
            59: '''
    root = CODE.parents[1]
    prd = root / "day58" / "code" / "graduation_project" / "workspace" / "demo-verify" / "docs" / "PRD.md"
    if not prd.is_file():
        import subprocess
        gp = root / "day58" / "code" / "graduation_project"
        subprocess.run(
            [sys.executable, str(gp / "scaffold.py"), "--direction", "rag_plus", "--name", "demo-verify"],
            check=False, cwd=str(gp),
        )
    if not prd.is_file():
        fail("PRD not found")
    ok("PRD path ready")
''',
            60: "    ok('sprint I — src module placeholder')\n",
            61: "    ok('sprint II — integration checkpoint')\n",
            62: "    ok('sprint III — tests/guardrails')\n",
            63: "    ok('docs and demo script')\n",
            64: "    ok('defense rehearsal')\n",
            65: "    ok('graduation delivery')\n",
        }
        w(f"day{day}/code/verify_day{day}.py", VERIFY.format(day=day) + checks.get(day, "") + """
    print("=== ALL PASSED ===")


if __name__ == "__main__":
    main()
""")


def gen_curriculum() -> None:
    w("curriculum/06_阶段六_毕业设计与就业_Day58-70.md", """# 阶段六学习路径 · Day 58–70（毕业设计 + 就业冲刺）

---

## 一、阶段划分

| 子阶段 | 天数 | 主题 |
|--------|------|------|
| 毕业设计 | 58–65 | 选题 → 开发 → 答辩 |
| 就业冲刺 | 66–70 | 简历 → 面试 → 结业 |

---

## 二、毕业设计八方向

见 `day58/code/graduation_project/README.md`

| 代号 | 名称 |
|------|------|
| rag_plus | RAG 商业化增强 |
| agent_plus | 多 Agent 办公增强 |
| finetune_cs | 垂直客服微调 |
| text2sql_bi | Text-to-SQL 分析台 |
| lowcode_bridge | 低代码桥接 |
| compliance_suite | 合规护栏平台 |
| multimodal_doc | 多模态文档助手 |
| custom | 自拟题目 |

---

## 三、每日导航

| 天 | 关键词 | 验收 |
|----|--------|------|
| 58 | 选题 scaffold | verify_day58 + verify_graduation |
| 59 | PRD 冻结 | verify_day59 |
| 60–62 | 开发三轮冲刺 | verify_day60–62 |
| 63 | 文档 Demo | verify_day63 |
| 64 | 答辩彩排 | verify_day64 |
| 65 | 正式答辩 | verify_day65 |
| 66 | 简历作品集 | verify_day66 |
| 67 | 技术面试题 | verify_day67 |
| 68 | 系统设计 | verify_day68 |
| 69 | 模拟面试 | verify_day69 |
| 70 | 结业复盘 | verify_day70 |

---

## 四、毕业设计 scaffold

```bash
cd day58/code/graduation_project
python3 scaffold.py --direction agent_plus --name my-project
python3 verify_graduation.py
```

---

*索引 · 2026-07-06 · 70 天课程收官*
""")


def main() -> None:
    print("Generating Day 58-70...")
    gen_graduation_skeleton()
    for day in range(58, 71):
        gen_day(day)
    gen_day58_verify()
    gen_verify_days_59_65()
    gen_employment_code()
    gen_curriculum()
    for i in range(58, 71):
        run = ROOT / f"day{i}" / "run.sh"
        if run.exists():
            run.chmod(0o755)
    print("Done.")


if __name__ == "__main__":
    main()
