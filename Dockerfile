# ============================================================
# Multi-stage Dockerfile for Physics AI
# Stage 1: Build frontend with Node
# Stage 2: Python runtime with Flask + built frontend
# ============================================================

# ── Stage 1: Build frontend ─────────────────────────────────
FROM node:20-alpine AS frontend-build

WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --production=false
COPY frontend/ ./
RUN npm run build

# ── Stage 2: Python runtime ─────────────────────────────────
FROM python:3.11-slim AS runtime

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy built frontend from Stage 1
COPY --from=frontend-build /app/frontend/dist /app/frontend/dist

# Nginx config — serve frontend static files + proxy API
RUN cat > /etc/nginx/sites-available/default <<'NGINX'
server {
    listen 80;
    server_name _;

    location / {
        root /app/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://127.0.0.1:5002;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /socket.io {
        proxy_pass http://127.0.0.1:5002;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    location /health {
        proxy_pass http://127.0.0.1:5002;
    }
}
NGINX

# Startup script — run both nginx and Flask
RUN cat > /app/start.sh <<'SH'
#!/bin/bash
set -e
nginx
exec python -m api.app
SH
RUN chmod +x /app/start.sh

EXPOSE 80 5002

ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

CMD ["/app/start.sh"]
