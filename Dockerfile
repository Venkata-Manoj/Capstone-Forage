# syntax=docker/dockerfile:1

# ============================================================
# Stage 1 — Build React frontend
# ============================================================
FROM node:22-alpine AS frontend-builder

WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# ============================================================
# Stage 2 — Python backend + serve built frontend
# ============================================================
FROM python:3.12-slim

LABEL maintainer="Venkata-Manoj"
LABEL description="CapstoneForge — AI-Powered Capstone Report Generation System"
LABEL org.opencontainers.image.source="https://github.com/Venkata-Manoj/Capstone-Forage"

WORKDIR /app

# System deps
RUN apt-get update && apt-get install --no-install-recommends -y \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# CPU-only PyTorch (saves ~2GB vs CUDA)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Python deps
COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Backend code
COPY backend/ .

# Built frontend
COPY --from=frontend-builder /app/dist ./static

# Patch main.py to serve frontend at /
COPY scripts/docker_patch_main.py /tmp/docker_patch_main.py
RUN python3 /tmp/docker_patch_main.py && rm /tmp/docker_patch_main.py

# Data directories
RUN mkdir -p uploads generated faiss_indexes

# Default env overrides for Docker
ENV PYTHONDONTWRITEBYTECODE=1 \
    SECRET_KEY=change-me-in-production \
    UPLOAD_DIR=./uploads \
    GENERATED_DIR=./generated \
    FAISS_INDEX_DIR=./faiss_indexes \
    LIBREOFFICE_PATH=/usr/bin/libreoffice \
    TESSERACT_CMD=/usr/bin/tesseract \
    DEBUG=false

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python3 -c "import requests; r=requests.get('http://localhost:8000/health', timeout=5); assert r.status_code == 200 and r.json().get('status') == 'healthy'" || exit 1

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
