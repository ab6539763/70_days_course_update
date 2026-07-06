# Day 22 补充讲义 · 前端调试与 Chrome DevTools

---

## 1. 打开 DevTools

- Windows/Linux：`F12` 或 `Ctrl+Shift+I`  
- Mac：`Cmd+Option+I`  
- 右键元素 →「检查」

## 2. Elements 面板

- 选中 `.bubble` 可在 **Styles** 侧边栏临时改 CSS  
- 改 `background` 即时预览，满意再抄回 `style.css`  
- **Computed** 查看最终盒模型：`padding`、`margin`、`width`

## 3. Console 面板

```javascript
// 在 Console 直接试
document.getElementById('message-list').children.length
pickMockReply('上海天气')
```

错误行号点击可跳到 `app.js` 对应行。

## 4. Network 面板（Day 24 必备）

过滤 `Fetch/XHR`，查看：

| 列 | 含义 |
|----|------|
| Status | 200 成功，4xx/5xx 错误 |
| Type | fetch |
| Response | 服务端 JSON |

**Failed to fetch** 常见原因：后端未启动、CORS、URL 写错。

## 5. 移动端模拟

DevTools → Toggle device toolbar（`Ctrl+Shift+M`）  
选 iPhone SE 375×667 检查响应式。

## 6. 常见错误

| 现象 | 原因 | 修复 |
|------|------|------|
| 点击发送无反应 | JS 报错或 id 不匹配 | 看 Console |
| 样式不生效 | 选择器优先级低 | 加 `.message.user .bubble` |
| fetch CORS | 跨域 | FastAPI CORSMiddleware |
| file:// fetch 失败 | 协议限制 | 用 `preview.sh` |

## 7. 与后端联调分工

```text
前端（你）     Network 里确认请求体、响应体
后端（Day24）  uvicorn 日志、FastAPI /docs
```

---

**一句话**：先 Console 查 JS，再 Network 查 HTTP——大模型全栈调试基本功。
