# Tool-53 AI Service

AI microservice for Tool-53 Security Controls Assessment.

Built with:
- Flask 3.x
- Groq LLM
- ChromaDB
- sentence-transformers
- Redis cache
- pytest
- OWASP ZAP verified

Port:
```text
5000
```

---

# Architecture

```text
Client / Spring Boot
        │
Flask AI Service
        │
 |──────┼───────────────|
Groq   Redis Cache    ChromaDB
LLM    SHA256 keys    RAG
```

---

# Prerequisites

Install:

- Python 3.11+
- pip
- Git

Optional:

- Redis 7
- OWASP ZAP

---

# Setup

## 1. Enter folder

```bash
cd ai-service
```

---

## 2. Create virtual environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / Mac

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Create .env

Create:

```text
.env
```

Example:

```env
GROQ_API_KEY=your_groq_key
REDIS_HOST=localhost
REDIS_PORT=6379
FLASK_ENV=development
```

---

# Environment Variables

| Variable | Required | Description |
|---|---|---|
| GROQ_API_KEY | yes | Groq API key |
| REDIS_HOST | no | Redis host |
| REDIS_PORT | no | Redis port |
| FLASK_ENV | no | development / production |

---

# Seed RAG Collection

Run once:

```bash
python services/rag_pipeline.py
```

This:

- loads `data/sample.txt`
- chunks text (500 chars, overlap 50)
- creates embeddings
- stores in ChromaDB

Chroma persistence:

```text
chroma_data/
```

Do NOT commit to Git.

---

# Run Service

```bash
python app.py
```

Health check:

```bash
curl http://localhost:5000/health
```

---

# API Reference

---

## GET /health

Returns:

- model name
- average response time
- uptime
- Chroma document count
- cache statistics

Example:

```bash
curl http://localhost:5000/health
```

---

## POST /describe

Analyzes a control.

### Request

```json
{
 "rule":"Admin accounts do not use MFA"
}
```

### Example

```bash
curl -X POST http://localhost:5000/describe -H "Content-Type: application/json" -d "{\"rule\":\"Admin accounts do not use MFA\"}"
```

---

## POST /recommend

Returns remediation recommendations.

### Request

```json
{
 "rule":"Passwords are weak"
}
```

---

## POST /categorise

Returns category and confidence.

### Request

```json
{
 "rule":"Audit logs disabled"
}
```

---

## POST /analyse-document

Extracts risks and findings.

### Request

```json
{
 "text":"Admin passwords are shared"
}
```

---

## POST /query

RAG semantic search.

### Request

```json
{
 "question":"How to secure passwords?"
}
```

---

## POST /generate-report

Default synchronous mode.

### Request

```json
{
 "input":"MFA missing"
}
```

Returns:

full report JSON

---

# Async mode

### Request

```json
{
 "input":"MFA missing",
 "async":true
}
```

Returns:

```json
{
 "job_id":"...",
 "status":"queued"
}
```

---

## GET /jobs/<job_id>

Returns:

- queued
- processing
- completed

---

## POST /batch-process

Processes up to 20 items.

### Request

```json
{
 "items":[
   {"rule":"MFA missing"},
   {"rule":"Logs disabled"}
 ]
}
```

---

# Security

Implemented:

- input sanitization
- SQL injection rejection
- prompt injection rejection
- XSS rejection
- rate limiting
- CSP headers
- X-Frame-Options
- X-Content-Type-Options

Validated using:

OWASP ZAP

Result:

- Critical: 0
- High: 0

---

# Testing

Run all tests:

```bash
pytest -v
```

Security tests:

```bash
pytest tests/test_security.py -s -v
```

Quality review:

```bash
python tests/quality_review.py
```

---

# Common Issues

## Redis unavailable

Behavior:

falls back to in-memory cache.

---

## Chroma empty

Run:

```bash
python services/rag_pipeline.py
```

---

## Groq authentication error

Check:

```text
GROQ_API_KEY
```

---

# Notes

Never commit:

```text
.env
chroma_data/
__pycache__/
```