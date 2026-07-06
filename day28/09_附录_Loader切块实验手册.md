# Day 28 附录 · Loader 与切块实验手册

> 含验收说明：`python3 verify_day28.py`

---

## 一、六种 Loader 对照

| Loader | 文件 | 典型元数据 | RAG 注意 |
|--------|------|------------|----------|
| TextLoader | .txt | source | 编码 UTF-8 |
| CSVLoader | .csv | row | 每行一 Document |
| UnstructuredMarkdown | .md | source | 保留标题 |
| PyPDFLoader | .pdf | page | 扫描件需 OCR |
| Docx2txt | .docx | - | 表格可能丢 |
| BSHTMLLoader | .html | title | 去 script 标签 |

---

## 二、chunk_size 实验记录表（学员填写）

| chunk_size | overlap | 块数 | 退款问题召回 | 备注 |
|------------|---------|------|--------------|------|
| 200 | 0 | | | |
| 500 | 50 | | | |
| 1000 | 100 | | | |

Day 31 `rag_tuning_lab.py` 将自动化此表。

---

## 三、RecursiveCharacterTextSplitter 分隔符优先级

```text
\n\n  →  \n  →  空格  →  字符
```

**意义**：尽量在段落边界切，避免句中切断专有名词。

---

## 四、process_pdf_ebook 输出 JSON 结构

```json
{
  "source": "ebook.pdf",
  "chunks": [
    {"index": 0, "content": "...", "metadata": {"page": 1}}
  ]
}
```

Day 29 `build_vectorstore.py` 可直接消费。

---

## 五、现场 15 题

1. PDF 无文字层怎么办？  
2. `len(doc.page_content)` 与 token 数关系？  
3. 为何 metadata 要存 `source`？（引用溯源 Day 30）  
4. 网页 Loader 内网 URL 风险？  
5. CSV 每行独立 chunk 的利弊？  

---

## 六、与 Day 11 文件 IO 衔接

Day 11 `open/read` → Day 28 Loader 抽象为 `Document` 对象 → Day 29 向量化。

---

*附录完。*
