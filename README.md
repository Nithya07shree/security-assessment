# Tool-53 — Security Controls Assessment

> AI-powered Security Controls Assessment platform built as an internship capstone project.
> Sprint: 14 April – 9 May 2026 | Demo Day: 9 May 2026

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT BROWSER                           │
│                    http://localhost (Port 80)                    │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTP / REST
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   REACT 18 + VITE FRONTEND                      │
│              Tailwind CSS │ Axios │ Recharts                    │
└─────────────────────────┬───────────────────────────────────────┘
                          │ REST API calls (JWT in header)
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│              SPRING BOOT 3 BACKEND (Port 8080)                  │
│   JWT Auth │ Redis Cache │ JavaMailSender │ Swagger UI          │
│   Flyway Migrations │ Spring Security │ JPA Auditing            │
└────────┬────────────────┬──────────────────────────────┬────────┘
         │                │                              │
         ▼                ▼                              ▼
┌─────────────┐  ┌─────────────────┐          ┌─────────────────┐
│ PostgreSQL  │  │   Redis 7       │          │  AI MICROSERVICE│
│     15      │  │ Cache 10min TTL │          │  Flask (Port    │
│  (Port 5432)│  │ AI Cache 15min  │          │     5000)       │
└─────────────┘  └─────────────────┘          │  Groq LLaMA-3.3 │
                                              │  ChromaDB RAG   │
                                              │  sentence-trans │
                                              └─────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Java 17, Spring Boot 3.x |
| Database | PostgreSQL 15 |
| Cache | Redis 7 |
| Migrations | Flyway |
| Security | Spring Security + JWT |
| Email | JavaMailSender + Thymeleaf |
| API Docs | Swagger / OpenAPI 3.0 |
| AI Service | Python 3.11, Flask 3.x |
| AI Model | Groq API (LLaMA-3.3-70b) |
| Vector DB | ChromaDB |
| Embeddings | sentence-transformers |
| Frontend | React 18 + Vite |
| Styling | Tailwind CSS |
| Charts | Recharts |
| Container | Docker + Docker Compose |

---

## Prerequisites

Before running this project, make sure you have:

- **Docker Desktop** — [docs.docker.com](https://docs.docker.com/get-docker/)
- **Docker Compose** — included with Docker Desktop
- **Git** — [git-scm.com](https://git-scm.com)
- **Groq API Key** — free at [console.groq.com](https://console.groq.com) (no credit card)

> Java, Python, and Node.js are NOT required locally — Docker handles everything.

---

## Setup Instructions

### Step 1 — Clone the repository

```bash
git clone https://github.com/tecsxpert/security-controls-assessment.git
cd security-controls-assessment
```

### Step 2 — Create your .env file

```bash
cp .env.example .env
```

Open `.env` and fill in all required values:

```env
# Database
DB_HOST=postgres
DB_PORT=5432
DB_NAME=tool53
DB_USERNAME=postgres
DB_PASSWORD=your_strong_password_here

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=

# JWT — generate with: openssl rand -base64 48
JWT_SECRET=your_minimum_32_character_secret_here
JWT_EXPIRATION_MS=86400000
JWT_REFRESH_EXPIRATION_MS=604800000

# Email
MAIL_HOST=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_FROM=noreply@tool53.com

# AI Service
AI_SERVICE_URL=http://ai-service:5000
GROQ_API_KEY=your_groq_api_key_here
```

### Step 3 — Start all services

```bash
docker-compose up --build
```

This starts all 5 services automatically:
- PostgreSQL 15
- Redis 7
- Spring Boot backend
- Flask AI microservice
- React frontend

Wait for this message:
```
backend  | Started Tool53Application in X seconds
```

### Step 4 — Access the application

| Service | URL |
|---|---|
| Frontend | http://localhost |
| Backend API | http://localhost:8080 |
| Swagger UI | http://localhost:8080/swagger-ui.html |
| AI Health | http://localhost:5000/health |

### Step 5 — Login with demo credentials

| Role | Email | Password |
|---|---|---|
| Admin | admin@tool53.com | Admin@123 |
| Manager | manager@tool53.com | Manager@123 |
| Viewer | viewer@tool53.com | Viewer@123 |

> 30 demo records are seeded automatically on first startup.

---

## Reset to Clean Demo State

```bash
docker-compose down -v
docker-compose up --build
```

This wipes all data and re-seeds 30 fresh demo records.
Run this before Demo Day.

---

## Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `DB_HOST` | ✅ | PostgreSQL host |
| `DB_PORT` | ✅ | PostgreSQL port (default 5432) |
| `DB_NAME` | ✅ | Database name |
| `DB_USERNAME` | ✅ | Database username |
| `DB_PASSWORD` | ✅ | Database password |
| `REDIS_HOST` | ✅ | Redis host |
| `REDIS_PORT` | ✅ | Redis port (default 6379) |
| `REDIS_PASSWORD` | ❌ | Redis password (optional) |
| `JWT_SECRET` | ✅ | Min 32-char Base64 secret |
| `JWT_EXPIRATION_MS` | ✅ | Token TTL in ms (86400000 = 24h) |
| `JWT_REFRESH_EXPIRATION_MS` | ✅ | Refresh token TTL |
| `MAIL_HOST` | ✅ | SMTP host |
| `MAIL_PORT` | ✅ | SMTP port |
| `MAIL_USERNAME` | ✅ | SMTP email address |
| `MAIL_PASSWORD` | ✅ | SMTP app password |
| `MAIL_FROM` | ✅ | From address for emails |
| `AI_SERVICE_URL` | ✅ | Flask AI service URL |
| `GROQ_API_KEY` | ✅ | Groq API key from console.groq.com |

---

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/login` | Login — returns JWT |
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/refresh` | Refresh JWT token |

### Security Controls
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/controls/all` | Get all controls (paginated) |
| GET | `/api/controls/{id}` | Get control by ID |
| POST | `/api/controls/create` | Create new control |
| PUT | `/api/controls/{id}` | Update control |
| DELETE | `/api/controls/{id}` | Soft delete control |
| GET | `/api/controls/search?q=` | Search controls |
| GET | `/api/controls/stats` | Dashboard KPIs |
| GET | `/api/controls/export` | Export CSV |

### File Attachments
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/files/upload` | Upload file (max 10MB) |
| GET | `/api/files/{id}` | Download file |
| GET | `/api/files/{id}/metadata` | Get file metadata |

### AI Service
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/ai/describe` | AI description |
| POST | `/api/ai/recommend` | AI recommendations |
| POST | `/api/ai/categorise` | AI categorisation |
| POST | `/api/ai/generate-report` | Generate report (SSE streaming) |
| POST | `/api/ai/query` | RAG query |
| GET | `/api/ai/health` | AI service health |

---

## Running Tests

```bash
# Backend unit tests
cd backend
./mvnw test

# View coverage report
open target/site/jacoco/index.html
```

---

## Common Issues

| Issue | Fix |
|---|---|
| Port already in use | Run `docker-compose down` then retry |
| Database connection failed | Check `DB_PASSWORD` in `.env` |
| AI not responding | Check `GROQ_API_KEY` in `.env` |
| Empty database | Run `docker-compose down -v && docker-compose up` |

---

## Team

Tool-53 — Security Controls Assessment
Capstone Project | TecSxpert Internship 2026
Sprint: 14 April – 9 May 2026

---

> **Security Note:** Never commit `.env` to GitHub.
> All secrets must be in `.env` which is listed in `.gitignore`.