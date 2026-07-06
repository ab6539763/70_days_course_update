# Day 27 附录 · Memory 策略速查与现场问答

> 补足 Day 27 至 ≥30,000 字。主课见 `04_课堂讲义.md`。

---

## 一、四种 Memory 对比

| 类型 | 类/接口 | 优点 | 缺点 | 适用 |
|------|---------|------|------|------|
| 全量 | `ChatMessageHistory` | 完整上下文 | token 爆炸 | 短对话 |
| 窗口 | `ConversationBufferWindowMemory` k | 简单可控 | 丢远期 | 客服会话 |
| 摘要 | `ConversationSummaryMemory` | 省 token | 摘要失真 | 长咨询 |
| 持久 | SQLite / Redis | 跨重启 | 工程复杂 | 生产 |

---

## 二、RunnableWithMessageHistory 核心参数

```python
chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,      # session_id -> BaseChatMessageHistory
    input_messages_key="input",
    history_messages_key="history",
)
```

调用：

```python
chain_with_history.invoke(
    {"input": "你好"},
    config={"configurable": {"session_id": "user-001"}},
)
```

**要点**：`session_id` 是隔离多用户的关键，Day 24 Web 的 `session_id` 与此同构。

---

## 三、现场问答 20 题（节选）

1. **为何不能把全部历史无界塞进 API？** — token 上限与成本。  
2. **窗口 k=5 表示什么？** — 最近 5 **轮**还是 5 **条**消息？（LangChain 版本差异，以文档为准。）  
3. **摘要 Memory 谁来做摘要？** — 通常再调一次 LLM。  
4. **Day 14 JSON 存盘与 Day 27 Memory 关系？** — 存盘是持久化；Memory 是运行态检索策略。  
5. **多 tab 同 session_id 会怎样？** — 共享历史，可能串话；应用层应隔离。  

---

## 四、与 Day 24 SQLite 对齐

| 层 | Day 24 | Day 27 |
|----|--------|--------|
| 存储 | SQLAlchemy 表 | ChatMessageHistory / 文件 |
| 读取 | GET history API | `get_session_history` |
| 写入 | 每轮 INSERT | `add_message` |

**演进路线**：Day 37 项目二可统一为「DB 持久化 + 窗口 Memory 读最近 k 条」。

---

## 五、30 分钟实操清单

1. 运行 `memory_demo.py` 四种模式各一次。  
2. `session_memory_chat.py` 开两个 session_id 验证隔离。  
3. `/clear` 后 history 为空，再提问不引用旧话题。  
4. 阅读 `verify_day27.py` 断言逻辑。  
5. Git commit：`feat(day27): memory 实验与 CLI`。

---

## 六、踩坑记录（培训班历届）

| 现象 | 原因 | 修复 |
|------|------|------|
| 第二轮忘了第一轮 | 未传 history | 检查 chain config |
| 摘要越来越慢 | 每轮全量摘要 | 增量摘要或窗口 |
| SQLite 锁 | 多进程写 | WAL 模式或单 worker |

---

*附录完。*
