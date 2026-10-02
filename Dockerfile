# ---------- Stage 1: build the Vue frontend ----------
FROM node:22-slim AS frontend
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
# The chessboard's CSS/piece SVGs aren't committed to the repo, so pull them
# from the npm package into public/ before building (same as `npm run copy-assets`).
RUN mkdir -p public/cm-chessboard && cp -r node_modules/cm-chessboard/assets/. public/cm-chessboard/
RUN npm run build

# ---------- Stage 2: Flask API + Stockfish + built frontend ----------
FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STOCKFISH_PATH=/usr/games/stockfish

RUN apt-get update \
    && apt-get install -y --no-install-recommends stockfish \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./
COPY --from=frontend /frontend/dist ./static

# Hosts like Render/Railway/Fly inject $PORT; default to 5000 locally.
# Analysis can take a while (Stockfish runs on every move), hence the long timeout.
EXPOSE 5000
CMD ["sh", "-c", "gunicorn app:app --bind 0.0.0.0:${PORT:-5000} --workers 1 --threads 4 --timeout 600"]
