# Week 5 阶段测验 · Day 39–44 Agent 专题综合回顾

> **说明**：闭卷 45 分钟。答案见 `07_作业参考答案.md`，测验期间不得查阅。

---

## 一、选择题（每题 2 分，共 30 分）

**1.** ReAct 范式中「Act」主要指？  
A. 激活 GPU  
B. 调用工具或执行环境动作  
C. 删除历史消息  
D. 仅生成 Markdown  

**2.** Agent 循环中 `tool` 角色消息的作用是？  
A. 装饰 system prompt  
B. 将工具执行结果回传给模型  
C. 替代用户输入  
D. 加密 API Key  

**3.** `max_iterations` 或 `max_rounds` 限制的主要目的是？  
A. 加速 embedding  
B. 防止死循环与成本失控  
C. 减少 chunk 数量  
D. 关闭流式输出  

**4.** LangGraph 相比单链 LCEL 的核心增强是？  
A. 只能做翻译  
B. 显式状态机与条件分支  
C. 不需要 Prompt  
D. 自动微调模型  

**5.** Agent + RAG 集成的典型模式是？  
A. 用向量库替代 LLM  
B. 将检索作为 Agent 的一个 tool  
C. 删除所有工具  
D. 只用 BM25  

**6.** Function Calling 的 `tools` schema 通常放在？  
A. HTTP Header  
B. 请求体的 `tools` 字段随 messages 发送  
C. 仅前端 localStorage  
D. SQLite 主键  

**7.** Planner-Executor 多 Agent 模式中 Planner 负责？  
A. 仅格式化 JSON  
B. 分解任务并编排步骤  
C. 训练 embedding  
D. 部署 Docker  

**8.** 低代码平台 Dify 的「工作流」节点最接近代码里的？  
A. 纯 CSS  
B. 有向图 / 状态机编排  
C. Git commit  
D. pytest fixture  

**9.** Coze（扣子）在国内场景的优势之一是？  
A. 只能跑 C++  
B. 与字节生态、国内模型接入较便捷  
C. 不支持 Bot 发布  
D. 无插件机制  

**10.** Agent 选择「自研代码」而非「Dify/Coze」的常见理由是？  
A. 低代码永远更快  
B. 需要深度定制、私有部署与 CI/CD 集成  
C. 不能使用 Python  
D. 不能接 API  

**11.** `messages[-20:]` 在 Agent 会话中用于？  
A. 删除 system  
B. 控制上下文窗口长度  
C. 随机采样  
D. 加密  

**12.** 工具描述（description）写不清楚会导致？  
A. embedding 维度变化  
B. 模型选错工具或根本不调用  
C. Chroma 损坏  
D. SSE 断开  

**13.** Human-in-the-loop 在 Agent 项目中指？  
A. 人工永远不写代码  
B. 敏感操作需人工审批后继续  
C. 关闭所有工具  
D. 仅用于单元测试  

**14.** Agent 轨迹（trace）记录主要用于？  
A. 生成前端 CSS  
B. 调试、审计与评测  
C. 替换数据库  
D. 压缩 PDF  

**15.** Week 5 综合助手 `integrated_agent_review.py` 演示了？  
A. 仅单轮问答  
B. 多工具 ReAct 环 + 知识检索  
C. 模型微调  
D. Docker 编排  

---

## 二、判断题（每题 2 分，共 20 分）

**16.** Agent 工具越多，效果一定越好。（ ）  

**17.** mock 模式可以在无 API Key 时验证 Agent 编排逻辑。（ ）  

**18.** Dify 可以完全替代所有企业自研 Agent 代码。（ ）  

**19.** 将 RAG 检索封装为 tool 比硬编码在 system prompt 更灵活。（ ）  

**20.** LangGraph 的 checkpoint 可用于恢复中断的长任务。（ ）  

**21.** Coze 与 Dify 都支持可视化工作流编排。（ ）  

**22.** Agent 死循环时仅靠 `print` 足够用于生产排错。（ ）  

**23.** `tool_calls` 出现在 assistant 消息中。（ ）  

**24.** Week 5 测验不要求手写 LangGraph 全部 API。（ ）  

**25.** 低代码平台适合快速 PoC，复杂权限与审计常需代码扩展。（ ）  

---

## 三、简答题（每题 5 分，共 25 分）

**26.** 用三句话说明 ReAct 中 Reasoning 与 Acting 如何交替。  

**27.** 对比 Dify 与自研 Python Agent 各举一个适用场景。  

**28.** 解释为何 Agent 需要 `max_rounds` 限制，并举一个不设限制的风险。  

**29.** `search_knowledge` 作为 tool 时，输入输出应如何设计？  

**30.** 说明 mock LLM 在培训与 CI 中的价值。  

---

## 四、实操题（25 分）

**31.**（10 分）运行 `integrated_agent_review.py --demo`，截图四条 demo 输出。  

**32.**（8 分）在 `dify_workflow_notes.md` 第三节补全你与 Dify/Coze 对比表的一行「私有部署」。  

**33.**（7 分）用一句话说明：项目二知识库（Day 36–38）若迁移到 Dify，你会保留哪一层自研？  

---

*测验结束。请将答卷文件名命名为 `week5_quiz_姓名.md` 提交。*
