# Day 25 Code · LangChain 入门

## 文件说明

| 文件 | 说明 |
|------|------|
| `mock_llm.py` | `FakeListChatModel` / `ChatOpenAI` 工厂 |
| `prompt_templates_lc.py` | `PromptTemplate` / `ChatPromptTemplate` 示例 |
| `langchain_chat.py` | **Day 14 CLI 的 LangChain 重写** |
| `verify_day25.py` | 自动化验收 |

## 快速开始

```bash
cd day25
bash run.sh

# 或
cd day25/code
pip install -r requirements.txt
python langchain_chat.py
python verify_day25.py
```

## 与 Day 14 对照

| Day 14 | Day 25 |
|--------|--------|
| `project1/llm_client.py` | `mock_llm.py` + `ChatOpenAI` |
| `project1/session.py` | `LangChainSession` + LangChain Messages |
| `project1/main.py` REPL | `langchain_chat.py` |
| 手写 messages dict | `ChatPromptTemplate` + `MessagesPlaceholder` |
