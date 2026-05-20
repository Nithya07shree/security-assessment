# Docker deployment

Run the full stack (frontend + Flask AI service + Redis) with Docker Compose.

## Prerequisites

- [Docker Desktop](https://docs.docker.com/get-docker/) (includes Docker Compose)
- A [Groq API key](https://console.groq.com)

## Quick start

### 1. Create environment file

From the project root:

```bash
cp .env.example .env
```

Edit `.env` and set your key:

```env
GROQ_API_KEY=your_actual_groq_key
```

### 2. Build and start

```bash
docker compose up --build
```

The **first build** can take 10–20 minutes (downloads Python ML dependencies and the embedding model).

### 3. Open the app

| URL | Service |
|-----|---------|
| http://localhost:8080 | React UI (production build via nginx) |
| http://localhost:8080/api/health | AI health (proxied to Flask) |

API calls from the browser go to `/api/*` → nginx → Flask on port 5000 inside the network.

## Useful commands

```bash
# Run in background
docker compose up --build -d

# View logs
docker compose logs -f

# Stop
docker compose down

# Stop and remove volumes (wipes Chroma + Redis data)
docker compose down -v
```

## Architecture

```
Browser → frontend:80 (nginx)
              ├── static files (Vite build)
              └── /api/* → ai-service:5000 (gunicorn + Flask)
                                    ├── Groq API
                                    ├── ChromaDB (volume: chroma_data)
                                    └── Redis (optional cache)
```

## What each container does

| Service | Replaces local command |
|---------|------------------------|
| `frontend` | `npm run build` + nginx (not `npm run dev`) |
| `ai-service` | `gunicorn` serving Flask (not `python app.py` dev server) |
| `redis` | Optional cache (falls back to in-memory if unavailable) |

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `ai-service` unhealthy / slow start | Wait up to 3 min on first run; check `docker compose logs ai-service` |
| `GROQ_API_KEY` errors | Verify `.env` in project root (same folder as `docker-compose.yml`) |
| Port 8080 in use | Change `8080:80` to `3000:80` under `frontend.ports` in `docker-compose.yml` |
| Out of disk / memory | AI image is large (~2GB+); allocate 4GB+ RAM to Docker Desktop |

## Production notes

- Do not commit `.env` or `chroma_data/` to git.
- For cloud hosting, push images to a registry and run the same `docker-compose.yml` on any VM with Docker (AWS EC2, DigitalOcean, etc.).
- Vercel cannot run this stack; use Docker on a VPS or a container platform (Railway, Render, Fly.io with Docker).
