# Claude-Cloud

Template project API Claude menggunakan Node.js (TypeScript) dan Python (FastAPI).

## Struktur Project

```
Claude-Cloud/
├── node/           → REST API dengan Express + TypeScript
│   ├── src/index.ts
│   ├── package.json
│   └── tsconfig.json
└── python/         → REST API dengan FastAPI
    ├── main.py
    └── requirements.txt
```

## Endpoint API

Kedua versi memiliki endpoint yang sama:

| Method | Endpoint       | Deskripsi                     |
|--------|---------------|-------------------------------|
| GET    | /             | Health check                  |
| POST   | /chat         | Chat sederhana (1 prompt)     |
| POST   | /conversation | Multi-turn dengan history     |
| POST   | /stream       | Streaming response (SSE)      |

## Cara Pakai

### Node.js

```bash
cd node
cp .env.example .env        # isi ANTHROPIC_API_KEY
npm install
npm run dev                 # development
npm run build && npm start  # production
```

### Python

```bash
cd python
cp .env.example .env        # isi ANTHROPIC_API_KEY
pip install -r requirements.txt
python main.py              # development (auto-reload)
```

## Contoh Request

```bash
# Chat sederhana
curl -X POST http://localhost:3000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Apa ibu kota Aceh?"}'

# Multi-turn
curl -X POST http://localhost:3000/conversation \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Halo, perkenalkan dirimu"},
      {"role": "assistant", "content": "Halo! Saya asisten AI."},
      {"role": "user", "content": "Apa yang bisa kamu bantu?"}
    ]
  }'
```

## Deploy ke Cloud

- **Railway**: connect repo ini, set env `ANTHROPIC_API_KEY`
- **Render**: pilih folder `node/` atau `python/`, set env yang sama
- **Fly.io**: gunakan `fly launch` di dalam folder `node/` atau `python/`
