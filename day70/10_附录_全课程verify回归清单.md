# Day 70 附录 · 全课程 verify 回归清单

> 本清单与 `day70/code/verify_day70.py`、`course_regression.py` 配套，供结业前 **签字验收**。  
> 环境变量统一：`export SPARKTECH_MOCK=1`

---

## 第 0 节 · 回归策略说明

### 0.1 两级验收

| 级别 | 脚本 | 范围 | 耗时 |
|------|------|------|------|
| L1 轻量 | `verify_day70.py` | 能力地图 + 关键 verify 文件存在 | < 5s |
| L2 抽样 | `course_regression.py` | 子进程跑 7 个代表日 | 5–15min |
| L3 全量 | 手动按清单 | 各阶段代表日 + 毕设 | 可选 1h+ |

### 0.2 course_regression.py 抽样日

```python
SAMPLE_DAYS = [14, 36, 48, 51, 57, 58, 66]
```

| Day | 命令 cwd | 意义 |
|-----|----------|------|
| 14 | `day14/project1` | `python -m project1.main --demo-once` 项目一 |
| 36 | `day36/code/project2` | RAG 项目二 |
| 48 | `day48/code/project3` | 多 Agent 项目三 |
| 51 | `day51/code` | 微调选型周起点 |
| 57 | `day57/code` | Compose 全栈部署 |
| 58 | `day58/code/graduation_project` | 毕业设计 |
| 66 | `day66/code` | 就业简历链 |

---

## 第 1 节 · Phase 代表日 verify 清单

### 1.1 阶段一 · Python + Project1（Day 1–14）

- [ ] **Day 14** `cd day14/project1 && python -m project1.main --demo-once`  
- [ ] 项目一 README 可运行说明存在  

### 1.2 阶段二 · LLM 基础（Day 15–24）

- [ ] **Day 20**（代表）`day20/code/verify_day20.py` 若存在  
- [ ] Web Chat / 流式输出 Demo 可口述  

### 1.3 阶段三 · RAG + Project2（Day 25–38）

- [ ] **Day 36** `cd day36/code/project2 && python3 verify_project2.py`  
- [ ] **Day 29** Chroma 运维代表日（可选）`verify_day29.py`  
- [ ] **Day 32** 混合检索相关实验可引用  

### 1.4 阶段四 · Agent + Project3（Day 39–50）

- [ ] **Day 48** `cd day48/code/project3 && python3 verify_project3.py`  
- [ ] **Day 42** Checkpointer（模拟面试常见弱项）  

### 1.5 阶段五 · 微调部署（Day 51–57）

- [ ] **Day 51** `verify_day51.py`  
- [ ] **Day 53** `lora_math_demo.py` + `verify_day53.py`  
- [ ] **Day 55** `ab_summary.json` lift 门禁  
- [ ] **Day 56** vLLM Mock + 压测  
- [ ] **Day 57** `verify_day57.py` + Compose config  

### 1.6 毕业设计（Day 58–65）

- [ ] **Day 58** `cd day58/code/graduation_project && python3 verify_graduation.py`  
- [ ] 答辩材料：架构图 + Demo 脚本  

### 1.7 就业冲刺（Day 66–70）

- [ ] **Day 66** `resume_builder.py` + `verify_day66.py`  
- [ ] **Day 67** `code_interview_drills.py` + `interview_llm_100.md`  
- [ ] **Day 68** `architecture_canvas.py` + `verify_day68.py`  
- [ ] **Day 69** `mock_interview_runner.py` → `reports/mock_interview.json`  
- [ ] **Day 70** `verify_day70.py` + `70天能力地图.md`  

---

## 第 2 节 · 一键执行命令

```bash
# L1
cd /workspace/day70/code && export SPARKTECH_MOCK=1 && python3 verify_day70.py

# L2 抽样回归（结业推荐）
cd /workspace/day70/code && export SPARKTECH_MOCK=1 && python3 course_regression.py

# 就业周局部
for d in 66 67 68 69; do
  echo "=== day$d ==="
  (cd /workspace/day$d/code && python3 verify_day$d.py) || exit 1
done
```

期望输出均含 `=== ALL PASSED ===` 或 `dayN: OK`。

---

## 第 3 节 · 失败排错速查

| 现象 | 可能原因 | 处理 |
|------|----------|------|
| day48 FAIL | PYTHONPATH 未设 | `course_regression` 已设；手动时 `export PYTHONPATH=.` |
| day36 缺依赖 | 未装 requirements | `pip install -r requirements.txt` |
| day57 Docker | 无 Docker 守护进程 | 口述 + 仅 `verify_day57.py` 进程内测 |
| day66 fail bullets | PROJECTS < 3 或无 RAG | 恢复 `resume_builder.py` 默认 |
| day69 score too low | 修改 Mock 分数 < 60 | 调高 Round.score |
| 超时 120s | 冷启动慢 | 重跑；检查死循环 |

---

## 第 4 节 · 结业签字表（打印或 Issue 勾选）

```text
学员：____________  日期：____________  SPARKTECH_MOCK=1

[ ] L1 verify_day70.py 通过
[ ] L2 course_regression.py 七日全 OK
[ ] Project1 / Project2 / Project3 verify 通过
[ ] verify_graduation.py 通过
[ ] Day 66–69 就业 verify 通过
[ ] GitHub 作品集链接：________________
[ ] 模拟面试平均分：______（mock_interview.json）

导师签字：____________
```

---

## 第 5 节 · 与能力地图对照

`70天能力地图.md` 结业标准三条，与本清单映射：

1. **3 阶段项目 verify 全绿** → §1.1 Day14、§1.3 Day36、§1.4 Day48  
2. **毕业设计答辩通过** → §1.6 Day58（人工）+ verify_graduation  
3. **GitHub 作品集公开** → Day 66 附录（人工）+ 签字表链接  

---

## 第 6 节 · 结业后维护建议

- 每月第一个周一跑 `course_regression.py`  
- 依赖升级后先跑 L2 再改 README  
- 新 employer 要求 live demo 时，单独开 branch 接真 Key，**不破坏 Mock 主分支**  

---

## 第 7 节 · verify 脚本命名约定

| 模式 | 示例 | 说明 |
|------|------|------|
| `verify_day{N}.py` | `verify_day66.py` | 单日作业验收 |
| `verify_project{N}.py` | `verify_project2.py` | 阶段项目 |
| `verify_graduation.py` | day58 毕设 | 特殊命名 |
| 模块入口 | `project1.main --demo-once` | Day 14 无独立 verify 文件名 |

新增个人项目时建议沿用此命名，便于 `course_regression.py` 扩展 `SAMPLE_DAYS`。

---

## 第 8 节 · SPARKTECH_MOCK 环境变量说明

全课程 verify 默认 `os.environ.setdefault("SPARKTECH_MOCK", "1")`：

- **不依赖** 外网 API Key  
- **不依赖** 本地 GPU  
- 产出 **确定性** 结果，适合 CI  

真机演示前单独分支设 `SPARKTECH_MOCK=0` 并配置 `.env`，**不要**把 Key 提交进回归分支。

---

**小结**：verify 绿色是 **技能存在的最低证明**；结业不是口头声明，而是 `course_regression.py` 七行 `OK` 与签字表上一串勾选。
