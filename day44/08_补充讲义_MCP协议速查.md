# Day 44 补充讲义 · MCP 协议速查

## 核心消息（简化）

| 方法 | 方向 | 说明 |
|------|------|------|
| tools/list | Client → Server | 发现工具 |
| tools/call | Client → Server | 执行工具 |

## FastMCP 常用 API

```python
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("name")

@mcp.tool()
def my_tool(arg: str) -> str: ...

mcp.run(transport="stdio")
```

## 与 Function Calling 对比

| 维度 | Function Calling | MCP |
|------|------------------|-----|
| 边界 | 单次 LLM 请求 | 独立进程/服务 |
| 复用 | 绑定某 Agent | 多 Client 共享 |
| 传输 | 模型 API 内置 | stdio / HTTP SSE |

## 安全注意

- Server 只暴露最小工具面  
- 参数校验 + 鉴权（生产）  
- 敏感工具加 HITL（结合 Day 42 interrupt）

## 课堂 mock 策略

- `mcp_compat.py` 统一检测  
- verify 不强制安装 `mcp`  
- 有 SDK 时仍走真实 FastMCP 工具定义，行为一致
