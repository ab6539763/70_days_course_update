# Day 26 补充讲义 · LCEL 进阶与调试

## 1. stream 与 invoke

```python
for chunk in chain.stream({"question": "hi"}):
    print(chunk, end="", flush=True)
```

Parser 在 stream 模式下通常在 **末 chunk** 才完成 parse；教学 demo 优先用 `invoke`。

## 2. batch 并发

```python
chain.batch([{"question": "a"}, {"question": "b"}], config={"max_concurrency": 2})
```

## 3. 中间结果调试

```python
chain = prompt | llm
msg = chain.invoke({"question": "test"})  # 先不带 parser
```

或使用 `RunnableLambda` 打印：

```python
def debug(x):
    print("DEBUG:", x)
    return x

chain = prompt | RunnableLambda(debug) | llm | StrOutputParser()
```

## 4. JsonOutputParser 排错

| 问题 | 解决 |
|------|------|
| JSONDecodeError | prompt 强调「只输出 JSON」 |
| 缺字段 | `get_format_instructions()` 写入 prompt |
| Pydantic 校验失败 | 检查 mock 返回是否含全部字段 |

## 5. 与 Agent 预告

LCEL 链是 Agent 的「单步推理」子结构；Week 6+ 将把 `tool` 节点接入 Runnable 图。
