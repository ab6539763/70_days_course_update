# 星火智服 · 毕业设计骨架（Graduation Project）

> 源码树 **Single Source of Truth**；Day 58 选题后在此开发，Day 65 答辩演示同一路径。

## 八方向选题表

| # | 代号 | 名称 | 说明 |
|---|------|------|------|
| 1 | `rag_plus` | RAG 商业化增强 | 基于 Project2，加混合检索实验台/多租户 |
| 2 | `agent_plus` | 多 Agent 办公增强 | 基于 Project3，持久化 checkpointer + 真实邮件 |
| 3 | `finetune_cs` | 垂直客服微调 | 基于 Day51–57，真机 LoRA + vLLM |
| 4 | `text2sql_bi` | Text-to-SQL 分析台 | 基于 Day47，可视化报表 + 护栏 |
| 5 | `lowcode_bridge` | 低代码桥接 | Dify/Coze 工作流对接自研 API |
| 6 | `compliance_suite` | 合规护栏平台 | Day46 护栏全链路接入三项目 |
| 7 | `multimodal_doc` | 多模态文档助手 | PDF+图片 OCR + RAG |
| 8 | `custom` | 自拟题目 | 经导师批准的原创方向 |

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
