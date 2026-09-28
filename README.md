# Claude-Cloud 🤖

Template REST API untuk integrasi **Anthropic Claude API** — tersedia dalam **Node.js (TypeScript)** dan **Python (FastAPI)**.

## Fitur

- ✅ 3 endpoint siap pakai: chat, conversation, streaming
- ✅ TypeScript + Express (Node.js)
- ✅ FastAPI + Pydantic (Python)  
- ✅ Auto-docs di `/docs` (Python)
- ✅ Contoh multi-turn conversation
- ✅ Server-Sent Events untuk streaming

## Struktur

```
Claude-Cloud/
├── node/           → Node.js / TypeScript
│   ├── src/
│   │   └── index.ts
│   ├── package.json
│   └── tsconfig.json
└── python/         → Python / FastAPI
    ├── main.py
    └── requirements.txt
```

## Quick Start

### 1. Dapatkan API Key

Buka [console.anthropic.com](https://console.anthropic.com/settings/keys) → buat API key baru.

### 2. Node.js

```bash
cd node
cp .env.example .env
# Edit .env → isi ANTHROPIC_API_KEY
npm install
npm run dev
```

Server berjalan di `http://localhost:3000`

### 3. Python

```bash
cd python
cp .env.example .env
# Edit .env → isi ANTHROPIC_API_KEY
pip install -r requirements.txt
python main.py
```

Server berjalan di `http://localhost:8000`  
Auto-docs: `http://localhost:8000/docs`

## Endpoint

| Method | Path            | Deskripsi                          |
|--------|-----------------|------------------------------------|
| GET    | `/`             | Health check                       |
| POST   | `/chat`         | Chat sederhana satu prompt         |
| POST   | `/conversation` | Multi-turn dengan riwayat pesan    |
| POST   | `/stream`       | Streaming response (SSE)           |

## Contoh Request

```bash
# Chat sederhana
curl -X POST http://localhost:3000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Jelaskan apa itu AI dalam 2 kalimat"}'

# Ganti model
curl -X POST http://localhost:3000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Halo", "model": "claude-haiku-4-5", "max_tokens": 512}'
```

## Deploy

| Platform | Cara |
|----------|------|
| Railway  | Connect repo, pilih folder `node/` atau `python/`, set `ANTHROPIC_API_KEY` |
| Render   | New Web Service → pilih folder, set env |
| Fly.io   | `fly launch` di dalam folder yang dipilih |

---

Dibuat dengan ❤️ oleh [Acut](https://github.com/yahcutrizalyusuf-Acut)
