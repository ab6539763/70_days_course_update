# Day 29 Code

```bash
cd day29/code
pip install -r requirements.txt
export SPARKTECH_MOCK=1

python3 build_vectorstore.py
python3 similarity_search_demo.py
python3 verify_day29.py
```

## 模块

| 文件 | 用途 |
|------|------|
| `mock_embeddings.py` | mock / live Embeddings |
| `chroma_kb.py` | Chroma 知识库封装 |
| `build_vectorstore.py` | 从 Day 28 样本建库 |
| `similarity_search_demo.py` | 相似检索演示 |
| `verify_day29.py` | 自动化验收 |

默认读取 `../../day28/code/data/sample_docs`。
