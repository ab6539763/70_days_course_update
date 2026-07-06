# Week 3 阶段测验 · Day 15–20 综合回顾

> **说明**：闭卷 45 分钟。答案见 `07_作业参考答案.md`，测验期间不得查阅。

---

## 一、选择题（每题 2 分，共 30 分）

**1.** Day 15 引入 pytest 的主要目的是？  
A. 替代 Git  
B. 自动化回归，防止重构破坏已有行为  
C. 加速 GPU 训练  
D. 生成前端页面  

**2.** `messages[-10:]` 在大模型项目中常用于？  
A. 删除 system 消息  
B. 随机采样对话  
C. 截取最近 N 条消息控制 token  
D. 加密历史记录  

**3.** `temperature=0` 最适合哪类任务？  
A. 需要稳定、可复现输出的分类/抽取  
B. 诗歌创作  
C. 随机头脑风暴  
D. 所有任务默认值  

**4.** Prompt 四要素不包括？  
A. 角色  
B. 任务  
C. 约束与示例  
D. GPU 型号  

**5.** OpenAI JSON Mode 要求模型输出？  
A. 任意 Markdown  
B. 合法 JSON 对象  
C. 二进制流  
D. HTML 页面  

**6.** Function Calling 中 `tool_calls` 出现在？  
A. 用户消息  
B. system 消息  
C. 模型 assistant 消息  
D. HTTP 响应头  

**7.** SSE（Server-Sent Events）单行事件前缀是？  
A. `data: `  
B. `json: `  
C. `event: `  
D. `chunk: `  

**8.** `yield` 与 `return` 的核心区别？  
A. 无区别  
B. `yield` 可多次产出，函数变为生成器  
C. `return` 更快  
D. 只能用于 async  

**9.** 客户端遇到 HTTP 4xx 错误一般应？  
A. 无限重试  
B. 立即切换模型  
C. 忽略  
D. 不重试，修正请求参数  

**10.** httpx 异步流式读取常用？  
A. `requests.get`  
B. `pickle.load`  
C. `client.stream()` + 行迭代  
D. `os.read`  

**11.** `max_tokens` 限制的是？  
A. 输入 Prompt 长度  
B. 模型生成部分的最大 token 数  
C. 工具调用次数  
D. 会话保存文件大小  

**12.** few-shot 示例通常放在 Prompt 的？  
A. 任务说明之后、当前用户输入之前  
B. 仅 system 最后一行  
C. 工具 schema 内部  
D. HTTP Header  

**13.** Rich 库主要用于？  
A. 数据库 ORM  
B. 分布式训练  
C. 终端美化输出  
D. 容器编排  

**14.** OpenAI `tools` 参数中每个 tool 的类型描述使用？  
A. XML DTD  
B. JSON Schema  
C. Protobuf  
D. YAML only  

**15.** FastAPI 返回 SSE 流常用？  
A. `FileResponse`  
B. `RedirectResponse`  
C. `HTMLResponse` only  
D. `StreamingResponse`  

---

## 二、判断题（每题 2 分，共 10 分）

**16.** mock 模式对培训与 CI 环境没有价值。（ ）  

**17.** 工具执行结果必须写回 messages 再调模型，才能生成面向用户的回复。（ ）  

**18.** 流式输出时，仍应在结束后拼接完整文本存入 session。（ ）  

**19.** 截断对话历史时，system 消息应优先保留。（ ）  

**20.** `SPARKTECH_MOCK=1` 时仍应发起真实 OpenAI HTTP 请求。（ ）  

---

## 三、简答题（每题 5 分，共 25 分）

**21.** 用三步简述 Agent 工具调用环（从用户输入到最终回复）。

**22.** 为何 Day 21 `integrated_assistant.py` 默认使用关键词 mock 路由工具，而不是仅依赖 live API？

**23.** 解释 Day 20 HTTP SSE 与 Day 21 Python 生成器 `yield` 流式的关系与区别。

**24.** `ConversationSession.trim()` 为何保留 system 消息？若删掉会怎样？

**25.** Day 22 静态 Chat UI 与今日 CLI 综合助手如何衔接？Day 24 又做什么？

---

## 四、代码阅读（附加练习，不计入 25 题总分）

阅读以下片段，回答问题：

```python
def stream_tokens(text: str, *, chunk_size: int = 2):
    for i in range(0, len(text), chunk_size):
        yield text[i : i + chunk_size]
```

**R1.** `list(stream_tokens("hello"))` 在 `chunk_size=2` 时结果是什么？

**R2.** 为何循环里用 `yield` 而不是 `return text[i:i+chunk_size]`？

---

**答题纸**：姓名 __________  学号 __________  得分 __________
