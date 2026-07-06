# Day 37 补充讲义 · 引用展示与 SSE

## 1. 为何 citations 先于 delta？

**UX**：用户先看到「答案依据哪些文档」，建立信任，再阅读生成内容。  
**技术**：检索耗时通常短于生成，先返回 citations 可填充 UI 空白期。

## 2. 引用展示模式对比

| 模式 | 优点 | 缺点 |
|------|------|------|
| 底部徽章 | 实现简单 | 多引用时拥挤 |
| 行内 [1][2] | 学术风格 | 需解析 markdown |
| 右侧抽屉 | 可看全文 | 开发量大 |

本课采用 **底部徽章 + click 查看 snippet**。

## 3. SSE 与 EventSource

| 方式 | 适用 |
|------|------|
| EventSource | 仅 GET |
| fetch + ReadableStream | **POST** 聊天（本项目） |

## 4. 常见联调问题

| 现象 | 排查 |
|------|------|
| CORS 错误 | 检查 CORS_ORIGINS、API_BASE 端口 |
| 引用不显示 | Network 看是否有 citations 事件 |
| 上传 422 | FormData 字段名须为 `files` |
| chunk_count=0 | 检查 sample_docs 与 lifespan ingest |

## 5. 性能提示

- 文档列表可 30s 轮询或上传后手动刷新  
- 大 PDF 上传显示 progress（选做 XMLHttpRequest upload.onprogress）  

---

*补充讲义 · Day 37*
