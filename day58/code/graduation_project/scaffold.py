# -*- coding: utf-8 -*-
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
        f"# {name}\n\n方向: {direction}\n\n## 里程碑\n- [ ] PRD\n- [ ] 架构图\n- [ ] MVP\n- [ ] verify 全绿\n- [ ] 答辩 PPT\n",
        encoding="utf-8",
    )
    for d in ("docs", "src", "tests"):
        (target / d).mkdir(exist_ok=True)
    (target / "docs" / "PRD.md").write_text("# PRD\n\n## 用户故事\n\n## 验收标准\n", encoding="utf-8")
    (target / "docs" / "ARCHITECTURE.md").write_text("# 架构设计\n\n```mermaid\nflowchart LR\n  User --> API\n```\n", encoding="utf-8")
    (target / "tests" / "verify_project.py").write_text(
        '''# -*- coding: utf-8 -*-
"""毕业设计验收 — 学员扩展此文件。"""
import json
from pathlib import Path

def main():
    meta = json.loads((Path(__file__).resolve().parents[1] / "project_meta.json").read_text())
    assert meta.get("direction"), "direction required"
    print("[OK] graduation project structure")

if __name__ == "__main__":
    main()
''',
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
