# Day 3 补充讲义 · 循环模式与交互 CLI 最佳实践

## 一、三种循环模式速查

| 模式 | 写法 | 适用 |
|------|------|------|
| 固定次数 | `for i in range(n)` | 九九表、批量 API 分页 |
| 直到条件 | `while not done` | 猜数字、重试输入 |
| 无限 REPL | `while True` + `break` | 菜单、聊天助手 |

企业代码里 **`while True` + break** 在 CLI 中很常见，但函数内部优先用**有明确条件**的 `while` 提高可读性。

## 二、输入校验分层

推荐顺序（Day 8 前手工，之后 try/except）：

1. `strip()` 去空白  
2. 判空 → `continue`  
3. 判格式 → `isdigit()` 或尝试 `int()`  
4. 判范围 → `1 <= x <= 100`  

```python
def read_int_in_range(lo: int, hi: int, prompt: str) -> int:
    while True:
        raw = input(prompt).strip()
        if not raw.lstrip("-").isdigit():  # 简易版，不支持负数可去掉
            print("请输入整数")
            continue
        value = int(raw)
        if lo <= value <= hi:
            return value
        print(f"请输入 {lo}~{hi} 之间的整数")
```

## 三、斜杠命令协议（Day 14 预览）

| 命令 | Day 3 行为 | Day 14 行为 |
|------|------------|-------------|
| `/exit` | 退出菜单 | 保存并退出 REPL |
| `/clear` | ANSI 清屏 | 清空 messages |
| `/help` | 打印帮助 | 含模型名、token 说明 |
| `/history` | 占位 | 打印最近 N 轮 |

**约定**：命令大小写不敏感；用户普通问题**不要**以 `/` 开头，以免误触发。

## 四、清屏实现差异

```python
# Unix / macOS / 现代 Windows Terminal
print("\033[2J\033[H", end="")

# 跨平台
import os
os.system("cls" if os.name == "nt" else "clear")
```

集训教室若为 SSH，ANSI 通常可用；CI 日志环境可能乱码，作业用换行占位即可。

## 五、random 与可复现

```python
import random
random.seed(42)  # 调试时固定种子，交付演示可去掉
secret = random.randint(1, 100)
```

联调 API 时「可复现」同样重要（Day 16 `temperature=0`）。

## 六、嵌套循环复杂度直觉

九九表：外层 9 × 内层平均 5 ≈ 45 次，O(n²) 在 n=9 可忽略。  
Two Sum 暴力 O(n²)，n=10⁴ 可能超时；Day 5 学 dict 后 O(n)。

## 七、与 Day 4 list 的衔接

今日作业 `guesses.append(guess)` 预习 list。Day 4 待办：

```python
todos: list[str] = []
todos.append("完成 Day3 作业")
for i, task in enumerate(todos, 1):
    print(f"{i}. {task}")
```

## 八、本周剩余日程

| 日 | 主题 |
|----|------|
| Day4 | list 待办管理器 |
| Day5 | dict + JSON |
| Day6 | 函数重构本周 CLI |
| Day7 | 通讯录 + 周测 |

---

*本补充与 04 讲义、01–03 文档合计满足 Day3 字数与深度要求。*
