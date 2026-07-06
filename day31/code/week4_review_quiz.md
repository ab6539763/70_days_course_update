# Week 4 阶段测验 · Day 25–30 综合回顾（RAG 基础周）

> **说明**：闭卷 45 分钟。答案见 `07_作业参考答案.md`，测验期间不得查阅。

---

## 一、选择题（每题 2 分，共 30 分）

**1.** RAG 全称 Retrieval-Augmented Generation 的核心思想是？  
A. 只用预训练权重生成  
B. 检索外部知识再拼入 Prompt 生成  
C. 删除所有历史对话  
D. 仅做关键词搜索  

**2.** 文档 `chunk_overlap` 的主要作用是？  
A. 加密切块  
B. 避免语义在块边界被截断丢失  
C. 减少向量维度  
D. 加速 BM25  

**3.** `top_k=5` 表示检索返回？  
A. 5 个 token  
B. 相似度最高的 5 个文档块  
C. 5 次 API 重试  
D. 5 个 embedding 模型  

**4.** LangChain `RecursiveCharacterTextSplitter` 优先按什么切分？  
A. 随机位置  
B. 分隔符层级（段落→句子→字符）  
C. 仅固定 token  
D. GPU 显存  

**5.** 向量检索擅长？  
A. 精确 SKU 编号匹配  
B. 语义相近但措辞不同的问句  
C. 正则表达式  
D. SQL JOIN  

**6.** BM25 属于？  
A. 稠密向量检索  
B. 稀疏词频检索  
C. 图像检索  
D. 图神经网络  

**7.** Embedding 将文本映射到？  
A. 二维坐标  
B. 高维连续向量空间  
C. 布尔值  
D. Markdown  

**8.** Chroma / FAISS 在 RAG 中通常作为？  
A. 前端框架  
B. 向量索引存储  
C. 负载均衡器  
D. Git 服务器  

**9.** RAG 中「幻觉」风险在检索质量差时会？  
A. 降低  
B. 升高（模型仍可能编造）  
C. 不变  
D. 仅影响 BM25  

**10.** `Document(page_content=..., metadata={})` 中 metadata 常用于？  
A. 存储来源、页码、父文档 ID  
B. 替换 embedding  
C. 禁用检索  
D. 加密  

**11.** 余弦相似度衡量的是？  
A. 向量夹角（方向接近程度）  
B. 欧氏距离绝对值  
C. 词频 TF  
D. 编辑距离  

**12.** 增大 `chunk_size` 一般会导致？  
A. 单块更完整，但检索粒度变粗  
B. 向量维度变大  
C. BM25 失效  
D. top_k 自动增大  

**13.** Day 24 前后端联调中 SSE 前缀是？  
A. `data: `  
B. `vector: `  
C. `rag: `  
D. `chunk: `  

**14.** FastAPI `StreamingResponse` 适合？  
A. 流式输出 LLM token  
B. 仅上传文件  
C. 编译 C 扩展  
D. 向量训练  

**15.** mock embedding 在教学中的价值是？  
A. 无 Key 可跑通流程  
B. 替代生产模型  
C. 提高准确率  
D. 禁用 LangChain  

---

## 二、判断题（每题 2 分，共 10 分）

**16.** （ ）RAG 检索阶段可以用不同 embedding 模型，生成阶段必须用同一模型。  

**17.** （ ）chunk_size 越小，检索越精细，但上下文碎片可能增多。  

**18.** （ ）top_k 越大，送入 LLM 的上下文一定越准确。  

**19.** （ ）LangChain Retriever 接口统一了 vector / BM25 / hybrid 的调用方式。  

**20.** （ ）无 API Key 时 SparkTech 课程要求 mock 模式验收全绿。  

---

## 三、简答题（每题 5 分，共 20 分）

**21.** 列举影响 RAG 召回率的三个可调参数，并各用一句话说明影响。

**22.** 解释「检索到的片段」如何拼进 Prompt（四要素中的 Context 位）。

**23.** 对比向量检索与关键词检索各适合什么类型的用户问句。

---

## 四、实操题（40 分）

**24.**（15 分）运行 `rag_tuning_lab.py`，截图最佳 `chunk_size` / `top_k` / `embedding_model` 组合及 hit_rate。

**25.**（15 分）将 `top_k` 从 3 改为 10，观察某条查询的 top-1 片段是否变化；简述原因。

**26.**（10 分）在 `week4_review_quiz.md` 同目录提交错题订正笔记（≥3 条）。

---

**及格线**：80 分。测验后讲师讲评 30 分钟，下午进入 RAG 调参实验。
