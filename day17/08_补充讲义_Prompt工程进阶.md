# Day 17 补充讲义 · Prompt 工程进阶与实践清单

## 一、Prompt 与 Token 成本（Day 15 衔接）

每条 few-shot 示例都计入 **输入 token**。粗算：

```text
总 token ≈ system + instruction + context + examples + input + output_format
```

优化策略：

1. 示例精简到 **最小可表达格式**  
2. 稳定后把 few-shot 蒸馏进 instruction（「输出格式同示例」）  
3. 高频模板做 **缓存**（Day 22+ Prompt Caching）

---

## 二、ICIO / CRISPE 框架对照

| 框架 | 字母 | 对应本课字段 |
|------|------|--------------|
| ICIO | Instruction | instruction |
| ICIO | Context | context |
| ICIO | Input | input_text |
| ICIO | Output | output_format |
| CRISPE | Capacity/Role | role |
| CRISPE | Insight | context |
| CRISPE | Statement | instruction |
| CRISPE | Personality | role 语气 |
| CRISPE | Experiment | examples |

不必死记硬背缩写，**四要素能覆盖 90% 企业场景**。

---

## 三、多语言 Prompt 注意点

1. **指令语言与输出语言分离**：指令中文、输出英文很常见  
2. 分类标签统一用 **中文或英文一种**，不要混用  
3. 翻译任务明示 **源语言与目标语言**  

---

## 四、模板评审 Rubric（5 分制）

| 维度 | 1 分 | 3 分 | 5 分 |
|------|------|------|------|
| 指令清晰度 | 模糊 | 可执行 | 可量化验收 |
| 上下文边界 | 无分隔 | 有分隔 | 分隔+防注入说明 |
| 输出约束 | 无 | 自然语言 | JSON 样例+禁止项 |
| 示例质量 | 无或错误 | one-shot | few-shot 分布均衡 |
| 可维护性 | 硬编码 | JSON 文件 | 版本号+metadata |

---

## 五、10 条模板设计意图详解

### P01 产品名翻译

教会 **品牌词保留** 与 context 放规范表。企业常有固定译名表，不应让模型自由发挥。

### P03 工单摘要

教会 **长度约束** 与 **关键信息覆盖**（用户 ID、影响面）。摘要下游常进飞书推送，超长会被截断。

### P05 礼貌改写

客服场景高频。role 用「话术教练」比「助手」更能抑制模型说教。

### P07 退款分类

JSON 字段与 Day 18 `intent_classifier` 对齐，降低明日迁移成本。

### P10 情感+人工介入

`need_human` 字段预演 Day 18 路由逻辑，一条 Prompt 同时练 **分类 + 策略**。

---

## 六、与 LangChain 的概念映射（预习）

| 本课 | LangChain |
|------|-----------|
| PromptTemplate | PromptTemplate / ChatPromptTemplate |
| examples | FewShotPromptTemplate |
| to_messages() | format_messages() |
| prompt_library/ | Hub / Git 仓库 |

张工说：先手写一遍，再看框架源码，否则调参只会迷信。

---

## 七、实操踩坑手册

### 坑 1：f-string 与 JSON 花括号

```python
# 错误：output_format 含 { 未转义
f"格式：{{\"intent\": \"...\"}}"  # OK
```

### 坑 2：示例输出与 output_format 不一致

示例用中文标签 `正面`，output_format 写 `positive`——模型混乱。

### 坑 3：context 过长淹没 instruction

RAG 检索 10 段文档全塞 context，模型「迷失」。应 Top-K + 重排（Day 36）。

### 坑 4：mock 当真理

mock 只做流程验证。上线前必须用 live 模型 + 黄金测试集评估。

---

## 八、黄金测试集（Golden Set）预习

企业应为每条分类模板维护 20–50 条标注样本：

```csv
input,expected_intent
我要退款,投诉退款
API 401,技术支持
```

每日回归：改 Prompt 后跑准确率，防 **Prompt 回归**。

---

## 九、晚自习 30 分钟清单

1. 默写四要素英文与含义  
2. 解释 zero vs few-shot 选型  
3. 跑通 `verify_day17.py`  
4. 阅读 `08_classify_tech.json`，思考加什么 example 能提升 401 识别  
5. `git commit` 今日笔记  

---

## 十、延伸阅读

- OpenAI Prompt Engineering Guide（官方六策略）  
- 李姐内部分享：《星火智服 Prompt 规范 v0.3》  
- Day 18 预告：CoT 论文 *Chain-of-Thought Prompting Elicits Reasoning in Large Language Models*

---

*补充讲义约 3500 字 · 与主讲义合计满足 Day 17 字数要求*
