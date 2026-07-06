# Day 30 Code · KEY DAY

```bash
cd day30/code
pip install -r requirements.txt
export SPARKTECH_MOCK=1

python3 rag_cli.py ingest
python3 rag_cli.py ask "如何申请退款？" --mock
python3 rag_cli.py chat --mock
python3 verify_day30.py
```

## RAG 全链路

```text
load → split → embed → store → retrieve → generate
```

| 文件 | 用途 |
|------|------|
| `rag_pipeline.py` | 核心流水线 + unknown 兜底 |
| `rag_cli.py` | CLI：ingest / ask / chat |
| `prompts/rag_prompt.txt` | RAG Prompt 模板 |
| `verify_day30.py` | KEY DAY 验收 |
