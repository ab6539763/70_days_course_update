# Day 26 附录 B · 晚自习 LCEL 链式调试

---

## 一、langsmith 预告（Day 46 详讲）

本地调试可先 `print` 每步：

```python
prompt_value = prompt.invoke({"q": "test"})
print(prompt_value.to_messages())
msg = llm.invoke(prompt_value)
print(msg.content)
```

---

## 二、stream 观察

```python
for chunk in (prompt | llm).stream({"q": "hi"}):
    print(chunk.content, end="")
```

---

## 三、batch 压测小实验

```python
inputs = [{"q": f"问题{i}"} for i in range(10)]
chain.batch(inputs)  # 观察耗时
```

---

## 四、Parser 失败重试模板

```python
from langchain_core.runnables import RunnableLambda

def safe_parse(text):
    try:
        return parser.parse(text)
    except Exception:
        return {"error": "parse_failed", "raw": text}

chain = prompt | llm | StrOutputParser() | RunnableLambda(safe_parse)
```

---

## 五、与翻译业务对齐的验收句

输入产品名 `星火智服工单系统`，链输出应：

- 含英文或日文（视链配置）  
- 无未替换 `{variable}`  
- 长度 < 500 字  

---

## 六、20 分钟练习

1. 给 `translation_chain.py` 加 `.stream` 打印  
2. 用 `PydanticOutputParser` 解析 `{title, summary}`  
3. 写 1 条 pytest：`assert "mock" in chain.invoke(...)`  

---

*晚自习完。*
