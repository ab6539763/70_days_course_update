# Day 28 补充讲义 · Loader 与切块进阶

## 1. 编码与乱码

| 场景 | 建议 |
|------|------|
| 中文 txt/md | `encoding="utf-8"` |
| GBK 老文件 | `encoding="gb18030"` 或 `chardet` 探测 |
| CSV | 指定 delimiter 与 quotechar |

Loader 失败时 **不要** `errors="ignore"` 静默丢字——日志记录并跳过该文件。

## 2. metadata 设计规范（星火智服）

| 键 | 类型 | 说明 |
|----|------|------|
| `source` | str | 相对知识库根路径 |
| `format` | str | pdf/docx/md/csv/html |
| `page` | int? | PDF 页码 |
| `version` | str? | 文档版本号 |
| `department` | str? | 归属部门 |

Day 30 引用格式：`[来源: faq_refund.txt#chunk-3]`。

## 3. 生产级 Loader 对比

| Loader | 优点 | 缺点 |
|--------|------|------|
| PyPDFLoader | 轻量 | 无 OCR |
| Unstructured | 多格式统一 | 依赖重 |
| Docx2txtLoader | 快 | 丢格式 |
| WebBaseLoader | 真实网页 | 噪声多、需网络 |

## 4. 切块策略进阶

### 4.1 二级切块

```text
MarkdownHeaderTextSplitter（按标题）
        │
        ▼
RecursiveCharacterTextSplitter（超长节再切）
```

### 4.2 按 Token 切

中文约 1.5~2 字符/token，可用 `tiktoken` 或 LangChain `TokenTextSplitter` 对齐模型窗口。

### 4.3 语义切块（预览）

Embedding 相似度突变处切分——计算贵，适合高价值文档。

## 5. chunk_size 与召回

```text
query: "如何申请退款"
  chunk_size 过大 → 块含退款+物流+发票，向量模糊
  chunk_size 过小 → 「点击申请退款」与「填写原因」分两块，可能只召回半流程
```

Day 30 用 **Recall@K** 评估（query 集 ≥ 20 条）。

## 6. 安全注意

- Loader **不执行** 文档内脚本；HTML 用 BS4 取文本  
- 上传路径校验，防目录穿越 `../../etc/passwd`  
- 敏感字段（身份证、手机）入库前脱敏  

## 7. 与 Unstructured / LlamaIndex 对比

本课程用 **LangChain** 保持与 Day 29 Chroma、Day 30 RAG CLI 一致。概念互通：

- LlamaIndex `SimpleDirectoryReader` ≈ LangChain Loader  
- NodeParser ≈ TextSplitter  

---

**延伸阅读**：LangChain Document Loaders 官方文档；Day 29 Chroma 持久化路径。
