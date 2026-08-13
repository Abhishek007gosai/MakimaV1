# Makima Bot - Production Dockerfile (Koyeb / Render / Docker)
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8080

WORKDIR /app

# Minimal build tools (for some wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Dependencies first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code
COPY . .

# Non-root user
RUN useradd -m -u 1000 botuser \
    && chown -R botuser:botuser /app \
    && mkdir -p /app && chown botuser:botuser /app
USER botuser

# Platform health checks hit $PORT
EXPOSE 8080

# Simple process healthcheck (platforms may use their own)
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD python -c "import os,urllib.request; urllib.request.urlopen('http://127.0.0.1:%s/' % os.getenv('PORT','8080'), timeout=3)" || exit 1

CMD ["python", "main.py"]
