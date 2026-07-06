# Day 25 补充讲义 · LangChain 生态与版本速查

## 1. 版本说明（2026 课堂基线）

本课程锁定 **LangChain 0.3.x**：

```text
langchain>=0.3.0,<0.4
langchain-core>=0.3.0,<0.4
langchain-community>=0.3.0,<0.4
langchain-openai>=0.2.0,<0.4
```

0.2 → 0.3 主要变化：

- 更多能力下沉到 `langchain-core`  
- `langchain.schema` 迁移为 `langchain_core.*`  
- 推荐 LCEL 而非旧版 `LLMChain`  

## 2. 常用 import 对照

| 旧（0.1/0.2） | 新（0.3） |
|---------------|-----------|
| `from langchain.chat_models import ChatOpenAI` | `from langchain_openai import ChatOpenAI` |
| `from langchain.prompts import ChatPromptTemplate` | `from langchain_core.prompts import ChatPromptTemplate` |
| `from langchain.schema import HumanMessage` | `from langchain_core.messages import HumanMessage` |
| `from langchain.llms.fake import FakeListLLM` | `from langchain_community.chat_models.fake import FakeListChatModel` |

## 3. ChatModel vs LLM

| 类型 | 输入 | 输出 | 推荐 |
|------|------|------|------|
| LLM | 字符串 | 字符串 | 旧 completion 模型 |
| ChatModel | Message 列表 | AIMessage | **GPT-4/国产对话模型** |

星火智服项目统一使用 **ChatModel**。

## 4. Runnable 预览（Day 26）

所有 LangChain 组件实现 `Runnable` 接口：

```python
chain = prompt | llm | StrOutputParser()
chain.invoke({"user_input": "你好"})
```

支持：`invoke` / `batch` / `stream` / `ainvoke`。

## 5. 排错清单

| 现象 | 处理 |
|------|------|
| `ImportError: langchain_openai` | `pip install langchain-openai` |
| `ValidationError` on invoke | 检查 `input_variables` 是否全部传入 |
| Fake 回复不按预期 | `FakeListChatModel` 按序循环，需自定义 responses |
| 与 Day 14 JSON 不兼容 | 检查 `role` 字段是否为 system/user/assistant |

## 6. 延伸阅读

- LangChain Concepts: https://python.langchain.com/docs/concepts/  
- Chat Models: https://python.langchain.com/docs/concepts/chat_models/  
- Prompt Templates: https://python.langchain.com/docs/concepts/prompt_templates/  

## 7. 课堂纪律

- Day 19 之前禁止 LangChain 是为了 **先懂底层**  
- Phase2 起 LangChain 为 **标准栈**，但需能脱离框架手写等价调用（面试常考）
