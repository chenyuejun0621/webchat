import os
import uuid
import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

DB_PATH = "data/chat.db"

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    """)
    conn.commit()
    conn.close()

init_db()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
)

app = FastAPI(title="WebChat")

SYSTEM_PROMPT = "你的代号是「武当修心」。说话沉稳简洁，像靠谱的朋友。短句，不废话，不油滑，不说教。坦诚。禁止表情符号。"


def _get_or_create_session(session_id: str | None) -> str:
    """获取或创建会话，返回 session_id。如果创建了新会话，自动写入 system prompt。"""
    conn = sqlite3.connect(DB_PATH)
    if session_id:
        row = conn.execute("SELECT id FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if row:
            conn.close()
            return session_id
    # 创建新会话
    new_id = uuid.uuid4().hex
    conn.execute("INSERT INTO sessions (id) VALUES (?)", (new_id,))
    conn.execute(
        "INSERT INTO messages (session_id, role, content) VALUES (?, 'system', ?)",
        (new_id, SYSTEM_PROMPT),
    )
    conn.commit()
    conn.close()
    return new_id


def _add_message(session_id: str, role: str, content: str):
    """存一条消息到数据库"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
        (session_id, role, content),
    )
    conn.commit()
    conn.close()


def _get_messages(session_id: str) -> list[dict]:
    """从数据库读取会话的所有消息"""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id",
        (session_id,),
    ).fetchall()
    conn.close()
    return [{"role": r, "content": c} for r, c in rows]


def _list_sessions() -> list[dict]:
    """列出所有会话，标题取第一条用户消息的前30字"""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id FROM sessions ORDER BY created_at DESC"
    ).fetchall()
    result = []
    for (sid,) in rows:
        user_row = conn.execute(
            "SELECT content FROM messages WHERE session_id = ? AND role = 'user' ORDER BY id LIMIT 1",
            (sid,),
        ).fetchone()
        title = user_row[0][:30] if user_row else "空会话"
        result.append({"id": sid, "title": title})
    conn.close()
    return result


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    session_id: str


@app.post("/chat")
def chat(req: ChatRequest) -> ChatResponse:
    sid = _get_or_create_session(req.session_id)
    _add_message(sid, "user", req.message)
    messages = _get_messages(sid)

    try:
        resp = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=messages,
            temperature=0.3,
            presence_penalty=0.3,
        )
        reply = resp.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    _add_message(sid, "assistant", reply)
    return ChatResponse(reply=reply, session_id=sid)


# 流式输出版（SSE）：AI 回复逐字返回，打字机效果
@app.post("/chat/stream")
def chat_stream(req: ChatRequest):
    sid = _get_or_create_session(req.session_id)
    _add_message(sid, "user", req.message)
    messages = _get_messages(sid)

    def generate():
        full_reply = ""
        try:
            stream = client.chat.completions.create(
                model="deepseek-v4-flash",
                messages=messages,
                stream=True,
                temperature=0.3,
                presence_penalty=0.3,
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
            _add_message(sid, "assistant", full_reply)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"X-Session-Id": sid},
    )


@app.get("/sessions")
def list_sessions():
    return _list_sessions()


# 托管前端页面（static 目录创建后生效）
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
