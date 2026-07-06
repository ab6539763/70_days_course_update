# Day 44 附录（二）· MCP 排错、安全清单与面试题

> 本文件为 Day 44 二级附录，配合 `09_附录_MCP协议速查.md` 使用。

---

## 一、Mock vs SDK 切换剧本

### 场景 1：课堂无网络

```bash
cd day44/code
python3 simple_mcp_server.py
# MCP SDK available: False → 正常
```

**台词**：「compat 层保证没装 mcp 也能学完协议语义。」

### 场景 2：答辩要真 Server

```bash
pip install mcp
python3 simple_mcp_server.py --stdio
```

另一终端用 Client 或 IDE 配置连接。

### 场景 3：list 与 call 不一致

若手动改 Mock 只加 list 未实现 call → `ValueError: unknown tool`。  
**检查**：`MockMCPServer._tools` 与 `call_tool` 分支同步。

---

## 二、agent_with_mcp 调试步骤

1. 打印 `plan_tools(question)` 计划列表  
2. 单独 `client.call` 每个工具，看 raw JSON  
3. 拼 `context_parts` 长度，防超 context  
4. 最后 LLM answer 是否引用 ticket_id / doc 名  

```python
trace = run_agent_with_mcp("工单 INC-2026-042 进展？")
for s in trace.steps:
    print(s.action, s.detail)
print(trace.tool_results)
```

---

## 三、安全清单（生产必读）

| 项 | 要求 |
|----|------|
| 鉴权 | Server 校验 Client token |
| 最小权限 | 工单 Server 不能读 KB |
| 输入校验 | ticket_id 正则白名单 |
| 输出脱敏 | 手机号打码 |
| 审计 | 每次 call_tool 写日志 |
| 超时 | Client 设 5s timeout |
| 限流 | 防 Agent 循环狂调 MCP |

---

## 四、FC / @tool / MCP 面试对照

| 面试问 | 答 |
|--------|-----|
| 何时 FC 够用？ | 单进程、工具少、无 IDE 共享 |
| 何时 @tool？ | LangChain 生态内快速集成 |
| 何时 MCP？ | 多 Client、跨语言、工具团队独立发布 |
| MCP 与 OpenAPI？ | OpenAPI 描述 HTTP；MCP 面向 Agent 会话与工具发现 |
| 如何做版本？ | Server 名带版本；list_tools 含 deprecated 标记 |

---

## 五、编码练习

### 练习 A：第三工具 escalate_ticket

在 `simple_mcp_server` 与 Mock 同时实现，Agent plan 检测「升级」关键词。

### 练习 B：ToolCallResult 重试

`SparkTechMCPClient.call` 失败重试 2 次，指数退避。

### 练习 C：LangChain 桥接

动态生成两个 @tool，用 `AgentExecutor` 跑同一问题，对比 `agent_with_mcp` 输出。

---

## 六、与 Day 40–43 串联问答

1. **Day 40 search_kb 与 MCP kb_search？** — 同业务；后者跨进程可共享给 Cursor。  
2. **Day 42 interrupt 能否等 MCP？** — 可以；interrupt 在 Agent 层，MCP 是工具层。  
3. **Day 43 Searcher 换 MCP 改几处？** — Searcher.run 内调用 Client，角色定义不变。  
4. **Checkpointer 存 MCP 结果吗？** — 存在 state/tool_results，非 MCP 协议本身。  

---

## 七、5 分钟 Demo 台词

1. 「集成爆炸：N Agent × M 后端，MCP 做工具总线。」  
2. `simple_mcp_server` 列出两工具，live call kb_search。  
3. `mcp_client_demo` 展示 parsed hits 数。  
4. `agent_with_mcp` 复合问题，指 trace.steps。  
5. 「项目三办公助手外围走 MCP。」

---

## 八、verify_day44 失败速查

| assert | 可能原因 |
|--------|----------|
| import | 路径未在 day44/code |
| list_tools 数量 | Mock 工具被改少 |
| call 返回 | JSON 格式变 |
| agent answer 空 | mock_llm 未配置 |

```bash
cd day44/code && python3 verify_day44.py -v 2>&1 | tail -20
```

---

## 九、stdio 与 HTTP/SSE 选型

| Transport | 优点 | 缺点 |
|-----------|------|------|
| stdio | 本地 IDE 集成简单 | 不宜远程 |
| SSE | 浏览器友好 | 要处理断连 |
| 自定义 HTTP | 与企业网关统一 | 非标准，互操作性差 |

星火内网推荐：**KB 走 SSE MCP**，工单走内网 stdio sidecar。

---

## 十、错误处理模板

```python
def safe_call(client, tool, **kwargs):
    try:
        return client.call(tool, **kwargs)
    except KeyError:
        return ToolCallResult(tool, kwargs, '{"error":"unknown_tool"}')
    except Exception as e:
        return ToolCallResult(tool, kwargs, json.dumps({"error": str(e)}))
```

Agent 汇总时识别 `error` 字段，提示用户而非幻觉。

---

## 十一、Phase3 结业答辩建议提纲

1. 从 Day 39 到 44 演进一条线（5 min）  
2. 现场跑 `agent_with_mcp` + 展示 trace（3 min）  
3. 画 MCP + Supervisor 架构图（2 min）  
4. Q&A：MCP vs @tool、interrupt vs approval  

---

## 十二、MCP 生态扩展阅读（不含安装）

- Anthropic MCP 规范：tools / resources / prompts 三类能力  
- Cursor / Claude Desktop 配置范例  
- 社区 Server：GitHub、Postgres、Filesystem  

课堂不展开安装，答辩可引用「与 IDE 同款协议」。

---

## 十三、工具膨胀治理

当 `list_tools()` 超过 20 个：

- Agent 侧先 **分类 plan**，只 bind 子集  
- 或用 Supervisor 专设「工具调度」子 Agent  
- 避免一次性 bind 全部 MCP 工具导致选型错误  

---

*Day 44 二级附录完*
