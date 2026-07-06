# Day 28 Code

```bash
cd day28/code
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # 可选

python3 ensure_samples.py      # 生成 PDF / DOCX 样本
python3 doc_loader_demo.py
python3 text_splitter_demo.py
python3 process_pdf_ebook.py
```

## 文件说明

| 文件 | 用途 |
|------|------|
| `doc_loader_demo.py` | PDF/Word/MD/Web/CSV/TXT Loader |
| `text_splitter_demo.py` | Character vs Recursive + chunk_size 调参 |
| `process_pdf_ebook.py` | PDF 电子书切块导出 JSON |
| `ensure_samples.py` | 自动生成 ebook.pdf / policy.docx |
| `data/sample_docs/` | 星火智服样本知识库 |

## 依赖

- `langchain-community` Document Loaders
- `langchain-text-splitters` Text Splitter
- `pypdf` / `python-docx` 样本生成与解析
