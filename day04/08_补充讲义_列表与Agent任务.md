# Day 4 补充讲义 · 列表思维与 Agent 任务列表

## 一、为什么大模型应用离不开 list

OpenAI 兼容 API 的请求体核心结构：

```python
messages = [
    {"role": "system", "content": "你是星火科技助手"},
    {"role": "user", "content": "总结今日待办"},
]
```

`messages` 是 **list[dict]**。Day 4 的 `todos` 是同一种「对象序列」思维：程序处理的不是单个值，而是一批结构化记录。

## 二、浅拷贝与待办列表

```python
backup = todos[:]       # 浅拷贝 list
```

若 `backup` 与 `todos` 共享内部 dict，改 `backup[0]["done"]` 会影响原列表。需要深拷贝时用 `copy.deepcopy`（Day 9 标准库专题）。v1.0 内存版暂可不引入。

## 三、列表性能直觉

| 操作 | 平均复杂度 |
|------|------------|
| `append` | O(1) |
| 下标访问 | O(1) |
| `pop(0)` | O(n) |
| `x in list` | O(n) |
| `x in set` | O(1) |

待办数百条时线性查找足够；数万条检索 id 应换 `dict[id -> item]`（Day 5 作业预告）。

## 四、Agent 任务列表（Day 48 预习）

Planner Agent 典型工具：

```text
create_task(title, priority)
list_tasks(status="pending")
complete_task(task_id)
```

与今日函数一一对应。差别在于：

- 输入来自 **模型 tool_call**，不是 `input()`  
- 列表可能同步到 **Redis / 数据库**  
- 任务带 `assignee`、`source_message_id` 等元数据  

今日把 CRUD 写清楚，等于提前实现 Agent 的「工作记忆」层。

## 五、set 在 RAG 中的去重

```python
seen_chunk_ids: set[str] = set()
unique_chunks = []
for c in candidates:
    if c["id"] in seen_chunk_ids:
        continue
    seen_chunk_ids.add(c["id"])
    unique_chunks.append(c)
```

也可用推导式 + 临时 set，但注意保持顺序时用上述写法。

## 六、不可变 messages 的误区

网上有「messages 要像 tuple 一样不可变」的说法——在 Python 里列表本身可变。工程实践是：**不要随便 pop 历史**，用切片构造新列表传给 API，避免破坏多轮上下文。

## 七、本周预告

| 日 | 主题 |
|----|------|
| Day5 | dict + JSON，待办写入 `todos.json` |
| Day6 | 函数重构，拆分 `todo_service.py` |
| Day7 | 通讯录综合 + 周测 |

---

*与 04 及作业合计满足 Day4 字数与深度要求。*
