# Day 2 补充讲义 · 字符串性能与 Prompt 片段库

## 一、为什么电话必须用 str

整数 `13800138000` 在 Python 内没问题，但若区号 `038` 转 `int` 变 `38`。企业系统一律 **str 存号码、单号、工号**。

## 二、replace 的陷阱

`"aaa".replace("a", "b")` → `"bbb"`，默认替换全部。若需只换一次传第三参数 `count=1`。

## 三、敏感词替换与内容安全

星火智服上线前需过内容审核。`mask_sensitive` 是玩具版；生产用：

- 上游：用户输入过滤  
- 下游：模型输出审核 API  
- Day 57 安全专题展开  

## 四、split+join 与 RAG

```python
paragraphs = document.split("\n\n")
chunks = [" ".join(p.split()) for p in paragraphs if p.strip()]
```

Day 28 文档切分将在此基础上加 `chunk_size`。

## 五、本周预告

| 日 | 主题 |
|----|------|
| Day3 | if/while/for，猜数字游戏 |
| Day4 | list 待办管理器 |
| Day5 | dict + JSON，模拟 API |
| Day6 | 函数重构本周项目 |
| Day7 | 通讯录 + 周测 |

---

*与 04 及作业合计满足 Day2 字数要求。*
