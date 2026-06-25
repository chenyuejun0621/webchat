# 项目上下文

## 用户
- 陈月钧，济南大学 AI专业，2024级（28届，2028年毕业）
- 排名 20/105，GPA 4.0，CET-4 已过
- GitHub: chenyuejun0621
- 暑假目标：广州 Python后端/AI应用开发 实习，7月开始，3个月以上
- Python/C++基础，后端零基础起步
- 竞赛：蓝桥杯省二(C/C++)，睿康软件赛省三
- 实践：济南大学信息处网络维护员（一年）

## 项目 webchat
FastAPI + DeepSeek API 聊天应用 —— 简历核心项目

路径: `C:\Users\28333\webchat\`
GitHub: `https://github.com/chenyuejun0621/webchat.git`

### 文件结构
```
webchat/
├── main.py              # 后端：/chat /chat/stream /sessions
├── static/index.html    # 前端：科幻风格 + 首页展示页 + 聊天双屏
├── requirements.txt
├── Dockerfile           # 容器化
├── docker-compose.yml   # 一键启动
├── .dockerignore
├── .env .env.example .gitignore
├── 陈月钧_简历.docx     # 桌面也有一份
├── 面试知识点.docx
└── PROJECT_CONTEXT.md
```

### 当前配置
- 模型: deepseek-v4-flash, temperature: 0.3, presence_penalty: 0.3
- System prompt: 武当修心，沉稳简洁，短句不废话不说教，禁止表情
- 会话: 内存dict，API base: api.deepseek.com/v1

### 里程碑
- Day1: /chat 非流式 + 多轮对话
- Day2: /chat/stream SSE流式
- Day3: 前端聊天界面
- Day4: 科幻风格首页 + 过场动画 + 移动端适配
- Day5: Docker 容器化（已完成，DaoCloud镜像源可用）
- 下一步: 数据库/RAG/部署

### Docker 注意事项
- Docker Desktop 国内必须配镜像源（daocloud可用，1ms.run不稳定）
- 配在 Docker Desktop → Settings → Docker Engine → registry-mirrors
- 命令：docker compose up/down/build

### DeepSeek API 注意
- deepseek-chat = 旧别名，2026-07-24 停用
- v4-flash (13B) vs v4-pro (49B)
- API层无法改模型自称身份

## 求职状态
- 简历已完成（超级简历制作）
- Boss直聘海投中，28届受限，主动打招呼
- 打招呼模板：三句话（谁/能干啥/有证明）
- 证件照：美图秀秀/醒图/小程序
