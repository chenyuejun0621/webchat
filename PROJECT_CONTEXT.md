# 项目上下文

## 用户
- 济南大学 AI专业 大二下，GitHub: chenyuejun0621
- 方向：AI应用开发，非纯算法
- 暑假目标：简历项目 + 实习
- Python/C++基础，后端零基础起步

## 项目 webchat
FastAPI + DeepSeek API 聊天应用

路径: `C:\Users\28333\webchat\`
GitHub: `https://github.com/chenyuejun0621/webchat.git`

### 文件
```
webchat/
├── main.py            # 后端：/chat /chat/stream /sessions
├── static/index.html  # 前端聊天界面
├── requirements.txt
├── .env .env.example .gitignore
```

### 当前配置
- 模型: deepseek-v4-flash, temperature: 0.3, presence_penalty: 0.3
- System prompt: 武当修心，沉稳简洁，短句，不废话不说教，禁止表情
- 会话: 内存dict，API base: api.deepseek.com/v1

### 里程碑
- Day1: /chat + 多轮对话
- Day2: /chat/stream 流式SSE
- Day3: 前端页面 + 调优
- 下一步: Docker/数据库/RAG

### DeepSeek API 注意
- deepseek-chat = 旧别名，2026-07-24 停用
- v4-flash (13B) vs v4-pro (49B)
- API层无法改模型自称身份
