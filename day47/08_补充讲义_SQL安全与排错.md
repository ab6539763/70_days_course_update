# Day 47 补充讲义 · SQL 安全与排错

## 1. 常见攻击面

| 攻击 | 示例 | 防护 |
|------|------|------|
| 多语句 | `SELECT 1; DROP TABLE` | 拒绝 `;` 中间语句 |
| 写操作伪装 | `SELECT * FROM t; DELETE` | 关键字黑名单 |
| PRAGMA | `PRAGMA foreign_keys=OFF` | 黑名单 |
| 子查询写操作 | 教学库可限制仅单表简单查询（进阶） |

## 2. 生产增强

1. **只读数据库用户**：SQLite 可用 URI `?mode=ro`  
2. **LIMIT 强制**：`SELECT` 自动追加 `LIMIT 100`  
3. **表白名单**：仅允许 `customers` 等四表  
4. **人工确认**：大额聚合结果二次展示 SQL 供确认  

## 3. 排错清单

| 现象 | 检查 |
|------|------|
| 数据库不存在 | 先 `seed_sales_data.py` |
| 校验失败 | 打印 raw SQL，查关键字 |
| 结果为空 | JOIN 条件、过滤 segment 大小写 |
| mock 答非所问 | 扩展 `MockTextToSQL` 规则 |

## 4. 与 Day 48 工具化

```python
def tool_query_sales(question: str) -> str:
    return TextToSQLAgent().ask(question).summary
```

---

*架构：[03_架构与设计.md](./03_架构与设计.md)*
