import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
)

app = FastAPI(title="WebChat")

# 存在内存中的对话仓库，key 为 session_id
sessions: dict[str, list[dict]] = {}


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    session_id: str


@app.post("/chat")
def chat(req: ChatRequest) -> ChatResponse:
    # 没有 session_id 或找不到对应会话 → 创建新会话
    if not req.session_id or req.session_id not in sessions:
        req.session_id = uuid.uuid4().hex
        sessions[req.session_id] = [
            {"role": "system", "content": "你是 helpful assistant。"}
        ]

    messages = sessions[req.session_id]
    messages.append({"role": "user", "content": req.message})

    try:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
        )
        reply = resp.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    messages.append({"role": "assistant", "content": reply})
    return ChatResponse(reply=reply, session_id=req.session_id)


# 流式输出版（SSE）：AI 回复逐字返回，打字机效果
@app.post("/chat/stream")
def chat_stream(req: ChatRequest):
    if not req.session_id or req.session_id not in sessions:
        req.session_id = uuid.uuid4().hex
        sessions[req.session_id] = [
            {"role": "system", "content": "你是 helpful assistant。"}
        ]

    messages = sessions[req.session_id]
    messages.append({"role": "user", "content": req.message})

    def generate():
        full_reply = ""
        try:
            stream = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                stream=True,
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    text = chunk.choices[0].delta.content
                    full_reply += text
                    yield f"data: {text}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: [ERROR] {e}\n\n"
        finally:
            messages.append({"role": "assistant", "content": full_reply})

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"X-Session-Id": req.session_id},
    )


@app.get("/sessions")
def list_sessions():
    result = []
    for sid, msgs in sessions.items():
        user_msgs = [m["content"][:30] for m in msgs if m["role"] == "user"]
        title = user_msgs[0] if user_msgs else "空会话"
        result.append({"id": sid, "title": title})
    return result


# 托管前端页面（static 目录创建后生效）
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
