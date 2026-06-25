# 前端会话持久化：localStorage 讲解

## 背景

数据库持久化解决了「服务器重启数据不丢」。但前端每次打开页面都会创建新会话——浏览器不记得上次用的是哪个 session_id。需要前端也记住。

## localStorage 是什么

浏览器内置的键值存储（key-value），每个网站独立。类比：chat.db 是图书馆（存所有数据），localStorage 是口袋里的便签纸（只记关键信息）。

```
你的电脑
  ┌──────────────┐    ┌─────────────────┐
  │ 浏览器        │    │ Docker 容器      │
  │ localStorage  │    │ chat.db         │
  │ session_id    │    │ 全部聊天记录     │
  └──────────────┘    └─────────────────┘
       便签纸                图书馆
```

| 对比 | localStorage | SQLite |
|------|-------------|--------|
| 存在哪 | 浏览器里 | 服务器硬盘 |
| 谁访问 | 前端 JS | 后端 Python |
| 存什么 | 少量 key-value | 大量结构化表数据 |
| 本例用途 | `"current_session_id": "5f2930b7..."` | 全部消息 |

## 三个 API

```javascript
// 写
localStorage.setItem("key", "value");

// 读（没有则返回 null）
localStorage.getItem("key");

// 删
localStorage.removeItem("key");
```

**null**：JavaScript 里表示「明确无值」，不是空字符串，不是 undefined。

## 三处改动

### 改动一：页面加载时恢复 session_id

```javascript
// 旧
let sessionId = null;

// 新
let sessionId = localStorage.getItem('current_session_id') || null;
```

**逐词拆解：**

| 部分 | 意思 |
|------|------|
| `localStorage.getItem('current_session_id')` | 从便签纸读 session_id |
| `||` | 逻辑「或」：左边是 null/false/空 → 用右边的值 |
| `null` | fallback 值，便签纸里没有就为 null |

**`||` 的运作：**

```javascript
localStorage.getItem(...) 返回 "abc123" → "abc123" || null → "abc123"
localStorage.getItem(...) 返回 null      → null || null      → null
```

### 改动二：收到新 session_id 后保存

```javascript
// send() 函数内，收到服务器响应后
sessionId = resp.headers.get('X-Session-Id');           // 原来就有
localStorage.setItem('current_session_id', sessionId);  // 新增
```

- `resp.headers.get('X-Session-Id')`：从 HTTP 响应头取 session_id
- `localStorage.setItem(...)`：写进便签纸，下次打开页面时改动一自动读回

### 改动三：点「新对话」时清除

```javascript
function newSession() {
  sessionId = null;                               // 清空 JS 变量
  localStorage.removeItem('current_session_id');  // 撕掉便签纸
  messagesDiv.innerHTML = ...;                    // 清空聊天界面
}
```

**必须同步清理的原因：** 如果只清 `sessionId = null` 不清 localStorage，下次打开页面时改动一会把旧 session_id 读回来，等于没建新会话。

## 完整生命周期

```
第一次打开：
  localStorage 空 → sessionId = null
  → 发消息 → 后端返回 session_id: "abc123"
  → localStorage.setItem("current_session_id", "abc123")

关闭浏览器，重新打开：
  → localStorage.getItem("current_session_id") → "abc123"
  → sessionId = "abc123"
  → 发消息带 session_id → AI 读历史 → 记得你 ✅

点击「新对话」：
  → localStorage.removeItem("current_session_id")
  → sessionId = null
  → 重新开始
```
