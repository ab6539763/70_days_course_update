# Day 2 晚自习专题 · Prompt 字符串预备营

## 一、为什么 f-string 是 Prompt 工程的第一把刀

大模型应用开发中，**Prompt 本质上就是一段精心构造的字符串**。  
你在 Day 17 会系统学习 Prompt 设计四要素；今天在字符串课上就要形成肌肉记忆：

```python
system_role = "你是星火科技企业内部知识库助手。"
context = "【文档片段】年假规定：入职满一年享有 10 天年假。"
user_question = "培训生第一周有年假吗？"

prompt = f"""{system_role}

{context}

用户问题：{user_question}

请仅根据文档片段回答，不知道请说「资料中未提及」。"""
```

这段代码已经具备 RAG 雏形：**系统角色 + 检索上下文 + 用户问题 + 输出约束**。

---

## 二、分隔符与多段拼接

OpenAI 风格 `messages` 在 Day 12 才发 HTTP；今天先用字符串理解结构：

```python
parts = [
    "【系统】你是严谨的企业助手。",
    "【上下文】产品名：星火智服。",
    "【用户】介绍产品。",
]
full_prompt = "\n\n".join(parts)
```

`join` 的好处：段落列表可来自数据库、向量检索结果（Day 30）。

---

## 三、输出格式约束预演

要求模型输出 JSON 时，Prompt 里要有样例（Day 18 JSON Mode）：

```python
schema_hint = '{"intent": "咨询|投诉|其他", "confidence": 0.0}'
prompt = f"""对用户消息分类，只输出 JSON，不要 markdown 代码块。
格式示例：{schema_hint}
用户消息：{user_text}"""
```

注意：f-string 嵌入 `schema_hint` 时，若含 `{` 要转义或先用变量承载。

---

## 四、变量命名与 Prompt 可读性

差写法：

```python
p = f"{a}{b}{c}"  # 维护者看不懂 a b c
```

好写法：

```python
customer_prompt = f"""
订单号：{order_id}
用户等级：{vip_level}
问题描述：{issue_description}
"""
```

企业 Code Review 常因 Prompt 变量命名不清打回。

---

## 五、字符串长度与 token（Day 15 预习）

```python
text = "大模型应用开发"
char_len = len(text)  # 字符数 7
# token 数 ≠ 字符数；中文往往 1 字 1~2 token
```

成本估算用 token；切片防超长用字符或 token 工具 `tiktoken`（Day 15）。

---

## 六、实战：把清洗报告改成「可贴进飞书」格式

```python
def format_report_markdown(before: str, after: str) -> str:
    return f"""## 文本清洗报告
| 项目 | 内容 |
|------|------|
| 清洗前字数 | {len(before)} |
| 清洗后字数 | {len(after)} |
| 减少 | {len(before) - len(after)} |

**清洗前**
```
{before}
```

**清洗后**
```
{after}
```
"""
```

飞书/钉钉 Markdown 在 Day 36 项目汇报会用到。

---

## 七、20 分钟跟练清单

1. 用 f-string 写一段不少于 80 字的 HR 问答 Prompt。  
2. 用 `join` 把 3 个文档片段合成上下文。  
3. 对 `personal_info_card` 的 `name` 字段调用 `strip_edges` 并打印前后对比。  
4. 在 `text_cleaner` 里勾选 1,2,4 跑通敏感词样例。  
5. `git commit` 今日作业。

---

## 八、LeetCode 思维预热（字符串版，非必做）

**题**：给定字符串 `s`，统计单词数（单词由空格分隔，首尾空格忽略）。  
**思路**：`len(s.split())` —— 一行；或手动 `strip` 后遍历（练循环，Day 3）。

**题**：验证回文串，忽略大小写与非字母数字。  
**思路**：过滤 + 双指针（Day 3 循环）；今天可用 `s == s[::-1]` 理解切片。

---

## 九、第一周作业互评表（供 Day 7 使用）

| 维度 | 1 分 | 3 分 | 5 分 |
|------|------|------|------|
| 命名 | 大量 a,b | 基本语义化 | 与 PRD 字段一致 |
| 注释 | 无 | 关键处有 | 含需求追溯编号 |
| 清洗 | 无 | 仅 strip | 完整 pipeline |
| Git | 无提交 | 1 次 | 规范 message |

---

## 十、明日晨读材料

预习 Day 3 `README.md` 中「猜数字」需求，思考：

- 随机数从哪里来？（`random` 模块 Day 11 详讲，明日可先 `import random`）  
- 用户猜错后如何「继续猜」？—— `while`  
- 如何限制最多猜 7 次？—— 计数 + `break`  

---

*本专题约 2800 字。Day 2 全套材料总字数 ≥ 30000。*
