import express, { Request, Response } from "express";
import Anthropic from "@anthropic-ai/sdk";
import dotenv from "dotenv";

dotenv.config();

const app = express();
app.use(express.json());

const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

// ─── Types ────────────────────────────────────────────────────────────────────

interface ChatRequest {
  prompt: string;
  model?: string;
  max_tokens?: number;
  system?: string;
}

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface ConversationRequest {
  messages: Message[];
  model?: string;
  max_tokens?: number;
  system?: string;
}

// ─── Health Check ─────────────────────────────────────────────────────────────

app.get("/", (_req: Request, res: Response) => {
  res.json({ status: "ok", message: "Claude API Node.js Template berjalan" });
});

// ─── Endpoint: Chat Sederhana ─────────────────────────────────────────────────
// POST /chat
// Body: { "prompt": "Halo Claude" }

app.post("/chat", async (req: Request, res: Response) => {
  try {
    const { prompt, model, max_tokens, system } = req.body as ChatRequest;

    if (!prompt) {
      return res.status(400).json({ error: "Field 'prompt' wajib diisi" });
    }

    const message = await client.messages.create({
      model: model || "claude-sonnet-4-5",
      max_tokens: max_tokens || 1024,
      system: system || "Kamu adalah asisten yang membantu.",
      messages: [{ role: "user", content: prompt }],
    });

    const text =
      message.content[0].type === "text" ? message.content[0].text : "";

    return res.json({
      response: text,
      model: message.model,
      usage: message.usage,
    });
  } catch (error: unknown) {
    const err = error as Error;
    console.error("Error:", err.message);
    return res.status(500).json({ error: err.message });
  }
});

// ─── Endpoint: Multi-turn Conversation ───────────────────────────────────────
// POST /conversation
// Body: { "messages": [{ "role": "user", "content": "Halo" }] }

app.post("/conversation", async (req: Request, res: Response) => {
  try {
    const { messages, model, max_tokens, system } =
      req.body as ConversationRequest;

    if (!messages || !Array.isArray(messages) || messages.length === 0) {
      return res
        .status(400)
        .json({ error: "Field 'messages' wajib diisi dan berupa array" });
    }

    const response = await client.messages.create({
      model: model || "claude-sonnet-4-5",
      max_tokens: max_tokens || 1024,
      system: system || "Kamu adalah asisten yang membantu.",
      messages: messages,
    });

    const text =
      response.content[0].type === "text" ? response.content[0].text : "";

    return res.json({
      response: text,
      model: response.model,
      usage: response.usage,
    });
  } catch (error: unknown) {
    const err = error as Error;
    console.error("Error:", err.message);
    return res.status(500).json({ error: err.message });
  }
});

// ─── Endpoint: Streaming ──────────────────────────────────────────────────────
// POST /stream
// Body: { "prompt": "Ceritakan sejarah Aceh" }

app.post("/stream", async (req: Request, res: Response) => {
  try {
    const { prompt, model, max_tokens, system } = req.body as ChatRequest;

    if (!prompt) {
      return res.status(400).json({ error: "Field 'prompt' wajib diisi" });
    }

    res.setHeader("Content-Type", "text/event-stream");
    res.setHeader("Cache-Control", "no-cache");
    res.setHeader("Connection", "keep-alive");

    const stream = await client.messages.stream({
      model: model || "claude-sonnet-4-5",
      max_tokens: max_tokens || 1024,
      system: system || "Kamu adalah asisten yang membantu.",
      messages: [{ role: "user", content: prompt }],
    });

    for await (const chunk of stream) {
      if (
        chunk.type === "content_block_delta" &&
        chunk.delta.type === "text_delta"
      ) {
        res.write(`data: ${JSON.stringify({ text: chunk.delta.text })}\n\n`);
      }
    }

    res.write("data: [DONE]\n\n");
    return res.end();
  } catch (error: unknown) {
    const err = error as Error;
    console.error("Error:", err.message);
    return res.status(500).json({ error: err.message });
  }
});

// ─── Start Server ─────────────────────────────────────────────────────────────

const PORT = Number(process.env.PORT) || 3000;
app.listen(PORT, () => {
  console.log(`✅ Server berjalan di http://localhost:${PORT}`);
  console.log("📋 Endpoint tersedia:");
  console.log("   GET  /              → Health check");
  console.log("   POST /chat          → Chat sederhana");
  console.log("   POST /conversation  → Multi-turn conversation");
  console.log("   POST /stream        → Streaming response");
});
