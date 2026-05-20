FROM python:3.11-slim-bookworm

WORKDIR /app

# curl for container health checks
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Pre-download embedding model at build time (avoids delay on every new container)
ENV TRANSFORMERS_CACHE=/app/.cache/huggingface
ENV SENTENCE_TRANSFORMERS_HOME=/app/.cache/sentence-transformers
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

EXPOSE 5000

# Single worker: sentence-transformers + Chroma are memory-heavy
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "--timeout", "120", "app:app"]
