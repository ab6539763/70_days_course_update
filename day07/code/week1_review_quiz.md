# Week 1 复盘测验 & Day 7 周测试卷

> **使用说明**  
> - **第一章**：上午复盘口试/速答（讲师带领）  
> - **第二章**：下午笔试（60 分钟，闭卷）  
> - **第三章**：读代码题（含在笔试内）  
> - **第四章**：机试检查清单（与 PRD AC 对照）  
> - **第五章**：答案与解析（讲师课后发放，学员订正用）

---

## 第一章 · 上午复盘速答（20 题）

### A. 概念速答

1. Python 中 `type(3.14)` 的结果是什么？  
2. `bool("")` 和 `bool("0")` 分别是什么？  
3. 字符串 `"  hello  ".strip()` 的结果？  
4. `range(3)` 生成的序列包含哪些整数？  
5. `break` 和 `continue` 的区别？  
6. 列表 `[1,2,3]` 执行 `append(4)` 后长度？  
7. 元组能否 `append`？为什么？  
8. 集合 `set` 的主要用途？  
9. `dict` 的键有什么限制？  
10. `json.loads` 的参数类型？  

### B. 关联题

11. Day 1 信息卡片六字段，哪些适合用 `int`/`bool`？  
12. Day 2 清洗手机号常用哪类字符串操作？  
13. Day 4 待办 `id` 自增变量通常叫什么？  
14. Day 5 Mock API 中 `employees` 是什么类型？  
15. 通讯录为什么用 `list[dict]` 而不是单个 `dict`？  

### C. 纠错题（口头说明错在哪）

16. `if age = 18:`  
17. `for i in range(5): print(i)` 后 `print(i)` 在某些 Python 版本中的现象？（了解即可）  
18. `emp = {}; emp["name"]` 未赋值先访问  
19. JSON 文本：`{'name': '陈晓'}`  
20. `json.dump(data, "out.json")` 第二参数类型错误  

---

## 第二章 · 下午笔试

**考试时间：60 分钟 | 总分：100 分**

### 一、选择题（每题 3 分，共 60 分）

**1.** 下列哪个不是 Python 合法变量名？  
A. `_score`  B. `name2`  C. `2name`  D. `employee_id`

**2.** `print(f"{3 * 'ab'}")` 输出？  
A. `ababab`  B. `3ab`  C. 报错  D. `ab ab ab`

**3.** `3 // 2` 的结果是？  
A. `1.5`  B. `1`  C. `2`  D. `1.0`

**4.** 下列关于 `list` 的说法错误的是？  
A. 可变  B. 有序  C. 元素必须同类型  D. 可嵌套  

**5.** `d = {"a": 1}; d.get("b", 0)` 的值？  
A. `None`  B. 报错  C. `0`  D. `""`

**6.** 下列 JSON 合法的是？  
A. `{name: "陈晓"}`  
B. `{"active": true}`  
C. `{"tags": (1,2)}`  
D. `{"x": undefined}`

**7.** `json.load(f)` 中 `f` 应该是什么？  
A. 文件路径字符串  B. 已打开的文件对象  C. dict  D. bytes  

**8.** `while` 循环至少执行几次体？（条件初始为 False）  
A. 0  B. 1  C. 无限  D. 看 break  

**9.** 列表推导式 `[x*2 for x in range(3)]` 的结果是？  
A. `[0,2,4]`  B. `[2,4,6]`  C. `[1,2,3]`  D. 生成器  

**10.** `contacts` 是 `list[dict]`，按 `id==3` 查找应？  
A. `contacts[3]`  B. `contacts["id"]`  C. 遍历比较 `c["id"]`  D. `dict(contacts)`  

**11.** `del lst[0]` 和 `lst.pop(0)` 的主要区别？  
A. 无区别  B. `pop` 返回被删元素  C. `del` 返回元素  D. 都不能删首项  

**12.** `ensure_ascii=False` 在 `json.dump` 中的作用？  
A. 加快写入  B. 中文不转 `\u` 转义  C. 压缩文件  D. 加密  

**13.** 函数定义中 `-> int` 表示？  
A. 强制返回 int  B. 返回类型注解  C. 参数类型  D. 文档  

**14.** `if __name__ == "__main__":` 的作用是？  
A. 定义主函数  B. 仅脚本直接运行时执行  C. 导入时必执行  D. 调试开关  

**15.** Day 7 退出通讯录前自动 `save` 主要解决？  
A. 加快启动  B. 数据持久化  C. 加密  D. 网络同步  

**16.** 下列哪个适合用 `set`？  
A. 保持插入顺序的唯一标签  B. 去重标签  C. 固定配置项  D. JSON 序列化  

**17.** `None` 在 JSON 中写作？  
A. `None`  B. `null`  C. `NULL`  D. `nil`  

**18.** `for i, x in enumerate(lst):` 中 `i` 是？  
A. 元素值  B. 索引  C. 副本  D. 长度  

**19.** 字符串 `"138 0013 8001".split()` 结果长度？  
A. 1  B. 2  C. 3  D. 4  

**20.** 通讯录 `next_id` 必须保存是因为？  
A. 装饰  B. 防止 id 重复  C. 压缩  D. 统计  

### 二、填空题（每题 2 分，共 20 分）

1. 获取用户输入的函数是 `_______`。  
2. 判断相等用 `_______` 运算符，赋值用 `_______`。  
3. 向列表尾部添加元素的方法：`list._______(item)`。  
4. 从字典安全取键，不存在时返回默认值：`dict._______(key, default)`。  
5. 将 JSON **字符串**解析为 Python 对象：`json._______(s)`。  
6. 将 Python 对象写入 JSON **文件**：`json._______(obj, f)`。  
7. 终止 `while` 循环的关键字：`_______`。  
8. 跳过本次循环剩余体、进入下一轮：`_______`。  
9. 单条联系人记录的类型：`_______`。  
10. 读取文件推荐指定编码：`open(path, encoding='_______')`。  

### 三、简答题（每题 10 分，共 20 分）

**1.** 简述 Day 4 内存待办与 Day 7 通讯录在「数据生命周期」上的区别。

**2.** 画出或文字描述：从 `contacts.json` 加载到 `add` 一条新联系人再到 `save` 的数据流（至少 6 步）。

---

## 第三章 · 读代码题（计入笔试）

### 读代码 1

```python
scores = [80, 90, 70]
total = 0
for s in scores:
    total += s
print(total / len(scores))
```

输出？若 `scores` 为空列表会怎样？

### 读代码 2

```python
data = '{"items": [{"id": 1, "ok": true}]}'
import json
obj = json.loads(data)
print(obj["items"][0]["ok"])
```

能否运行？若不能，错在哪？

### 读代码 3

```python
todos = [{"id": 1, "done": False}]
for t in todos:
    if t["id"] == 1:
        todos.remove(t)
todos.append({"id": 2, "done": False})
print(len(todos))
```

输出可能是什么？这种写法有何风险？（提示：遍历时修改 list）

### 读代码 4

```python
def find(contacts, name):
    for c in contacts:
        if c["name"] == name:
            return c
    return None

contacts = [{"id": 1, "name": "陈晓", "phone": "138"}]
print(find(contacts, "李雷"))
```

输出？

### 读代码 5

```python
x = 5
def foo():
    x = 10
    print(x)
foo()
print(x)
```

输出两行分别是什么？（Week 1 了解级）

---

## 第四章 · 机试检查清单

学员机试时在旁打勾：

| 步骤 | 操作 | ✓ |
|------|------|---|
| 1 | `python3 address_book.py` 无报错启动 | |
| 2 | 启动显示已加载记录数 | |
| 3 | add 新联系人成功 | |
| 4 | list 可见新记录 | |
| 5 | search 关键词命中 | |
| 6 | update 修改部门成功 | |
| 7 | delete 删除测试数据 | |
| 8 | quit 退出 | |
| 9 | 重启后数据仍在 | |
| 10 | `python3 -m json.tool contacts.json` 通过 | |

---

## 第五章 · 答案与解析

### 第一章速答

1. `<class 'float'>`  
2. `False`, `True`  
3. `"hello"`  
4. `0, 1, 2`  
5. `break` 退出循环；`continue` 进入下一轮  
6. `4`  
7. 不能，元组不可变  
8. 去重、成员检测、集合运算  
9. 必须可哈希，一般用 str/int/tuple  
10. `str`（JSON 格式字符串）  
11. `age`→int，`need_dorm`→bool，其余多 str  
12. `strip`、`remove_all_spaces` / `split`  
13. `next_id`  
14. `list`（元素为 `dict`）  
15. 多条联系人记录，需动态增删  
16. 赋值 `=` 不能用于 if 条件，应用 `==`  
17. 循环变量泄漏（Python 3 中 `i` 为 4）  
18. `KeyError`  
19. JSON 必须用双引号键和字符串  
20. 第二参应是文件对象，需 `open(...)`  

### 第二章笔试答案

**选择**：1C 2A 3B 4C 5C 6B 7B 8A 9A 10C 11B 12B 13B 14B 15B 16B 17B 18B 19C 20B  

**填空**：  
1. `input`  
2. `==`，`=`  
3. `append`  
4. `get`  
5. `loads`  
6. `dump`  
7. `break`  
8. `continue`  
9. `dict`（或字典）  
10. `utf-8`  

**简答要点**：  
1. Day 4 进程结束数据丢失；Day 7 通过 JSON 持久化，可跨会话保留。  
2. load 读文件 → json.load → contacts/next_id → 用户 add → append + next_id++ → save → json.dump 写文件。  

### 第三章读代码

1. 输出 `80.0`；空列表 `ZeroDivisionError`  
2. 不能；JSON 中 `true` 小写，`loads` 可解析；若写成 Python `True` 在 JSON 字符串里则非法——题目 JSON 合法，输出 `True`  
3. 可能 `1`（删了一条又 append）；风险：遍历时 `remove` 跳过元素  
4. `None`  
5. `10` 然后 `5`（局部 vs 全局）  

---

**讲师备注**：机试以实际运行结果为准；读代码 2 若学员质疑 JSON `true`，表扬并说明这正是 Day 5 重点。
