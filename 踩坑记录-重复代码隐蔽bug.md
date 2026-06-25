# 踩坑记录：重复代码导致的一个隐蔽 Bug

## 现象

修改 system prompt 后，前端聊天没有任何变化，AI 仍然使用旧的 system prompt。

## 排查过程

1. 检查代码逻辑 → 正确
2. 重启服务 → 无效
3. 清除浏览器缓存 + 开新会话 → 无效
4. 怀疑 DeepSeek 模型训练数据导致无法修改自称 → **错误判断**

## 真正原因

旧代码中 system prompt 在两个端点各定义了一次：

```python
# /chat 端点 — 第 123 行
{"role": "system", "content": "你的代号是..."}

# /chat/stream 端点 — 第 150 行
{"role": "system", "content": "你的代号是..."}
```

前端用的是 `/chat/stream`。修改时只改了 `/chat` 的那一份，漏掉了 `/chat/stream` 的另一份。

## 为什么重构后自动修复了

新代码将 system prompt 提取为单一变量 `SYSTEM_PROMPT`，两个端点通过 `_get_or_create_session` 共享同一份定义。消除了重复，也就不存在「改了一个漏了另一个」的问题。

```python
# 新代码：只定义一次
SYSTEM_PROMPT = "你的代号是..."

# 两个端点共享同一个逻辑
def _get_or_create_session(session_id):
    ...
    conn.execute("INSERT INTO messages ... VALUES (?, 'system', ?)", (new_id, SYSTEM_PROMPT))
```

## 教训

**重复代码不只是「不好看」，它会直接导致 Bug。** 同一个信息出现在多处，修改时必须手动同步，人是不可靠的。应该用单一数据源（Single Source of Truth）——定义一次，多处引用。
