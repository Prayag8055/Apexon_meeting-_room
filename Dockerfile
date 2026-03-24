# ============================================================
# Apexon RoomBook — Production Dockerfile
# Single container: nginx (React) + FastAPI backend
# ============================================================

# ── Stage 1: Build React frontend ────────────────────────────
FROM node:20-alpine AS frontend-build
WORKDIR /app
COPY react-app/package.json react-app/package-lock.json ./
RUN npm ci --production=false
COPY react-app/ ./
RUN npm run build

# ── Stage 2: Production image ────────────────────────────────
FROM python:3.12-slim

# Install nginx, supervisor, and envsubst (for PORT substitution)
RUN apt-get update && \
    apt-get install -y --no-install-recommends nginx supervisor gettext-base && \
    rm -rf /var/lib/apt/lists/*

# Python dependencies
WORKDIR /app
COPY room-booking-api/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY room-booking-api/ ./room-booking-api/
COPY run_api.py ./
COPY seed_admin.py ./
COPY seed_rooms.py ./

# Copy built React frontend
COPY --from=frontend-build /app/dist /usr/share/nginx/html

# Nginx config — serves React + proxies /api to FastAPI
COPY nginx.conf /etc/nginx/conf.d/default.conf
# Remove default nginx site
RUN rm -f /etc/nginx/sites-enabled/default

# Supervisor config — runs both nginx and uvicorn
COPY supervisord.conf /etc/supervisor/conf.d/app.conf

# Data directory for SQLite
RUN mkdir -p /data
ENV DB_PATH=/data/bookings.db

# Startup script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Render sets PORT dynamically; default 80 for local Docker
EXPOSE 80

CMD ["/docker-entrypoint.sh"]
