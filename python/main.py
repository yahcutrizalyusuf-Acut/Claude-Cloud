import os
from typing import AsyncIterator

import anthropic
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

load_dotenv()

app = FastAPI(
    title="Claude API - Python Template",
    description="Template REST API Python menggunakan FastAPI + Anthropic SDK",
    version="1.0.0",
)

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

DEFAULT_MODEL = "claude-sonnet-4-5"
DEFAULT_SYSTEM = "Kamu adalah asisten yang membantu."

# ─── Models ───────────────────────────────────────────────────────────────────


class ChatRequest(BaseModel):
    prompt: str
    model: str = DEFAULT_MODEL
    max_tokens: int = 1024
    system: str = DEFAULT_SYSTEM


class Message(BaseModel):
    role: str  # "user" atau "assistant"
    content: str


class ConversationRequest(BaseModel):
    messages: list[Message]
    model: str = DEFAULT_MODEL
    max_tokens: int = 1024
    system: str = DEFAULT_SYSTEM


# ─── Health Check ─────────────────────────────────────────────────────────────


@app.get("/")
def root():
    return {"status": "ok", "message": "Claude API Python Template berjalan"}


# ─── Endpoint: Chat Sederhana ─────────────────────────────────────────────────
# POST /chat
# Body: { "prompt": "Halo Claude" }


@app.post("/chat")
def chat(req: ChatRequest):
    try:
        message = client.messages.create(
            model=req.model,
            max_tokens=req.max_tokens,
            system=req.system,
            messages=[{"role": "user", "content": req.prompt}],
        )
        text = message.content[0].text if message.content else ""
        return {
            "response": text,
            "model": message.model,
            "usage": {
                "input_tokens": message.usage.input_tokens,
                "output_tokens": message.usage.output_tokens,
            },
        }
    except anthropic.APIError as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Endpoint: Multi-turn Conversation ───────────────────────────────────────
# POST /conversation
# Body: { "messages": [{ "role": "user", "content": "Halo" }] }


@app.post("/conversation")
def conversation(req: ConversationRequest):
    try:
        messages = [{"role": m.role, "content": m.content} for m in req.messages]
        response = client.messages.create(
            model=req.model,
            max_tokens=req.max_tokens,
            system=req.system,
            messages=messages,
        )
        text = response.content[0].text if response.content else ""
        return {
            "response": text,
            "model": response.model,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
        }
    except anthropic.APIError as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Endpoint: Streaming ──────────────────────────────────────────────────────
# POST /stream
# Body: { "prompt": "Ceritakan sejarah Aceh" }


@app.post("/stream")
def stream_chat(req: ChatRequest):
    async def generate() -> AsyncIterator[str]:
        with client.messages.stream(
            model=req.model,
            max_tokens=req.max_tokens,
            system=req.system,
            messages=[{"role": "user", "content": req.prompt}],
        ) as stream:
            for text in stream.text_stream:
                yield f"data: {text}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


# ─── Run (untuk development lokal) ────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    print(f"✅ Server berjalan di http://localhost:{port}")
    print("📋 Endpoint tersedia:")
    print("   GET  /              → Health check")
    print("   POST /chat          → Chat sederhana")
    print("   POST /conversation  → Multi-turn conversation")
    print("   POST /stream        → Streaming response")
    print(f"📖 Docs: http://localhost:{port}/docs")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
