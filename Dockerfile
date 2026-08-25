FROM node:22-alpine AS frontend

WORKDIR /build/frontend-vue
COPY frontend-vue/package.json frontend-vue/package-lock.json ./
RUN npm ci
COPY frontend-vue/ ./
RUN npm run build


FROM python:3.12-slim-bookworm

ENV UV_SYSTEM_PYTHON=1 \
    OPENBLAS_NUM_THREADS=1

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

RUN apt-get update \
  && apt-get install -y curl \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /weather
COPY uv.lock pyproject.toml /weather/

RUN uv sync --frozen --no-dev --no-install-project

COPY . /weather
COPY --from=frontend /build/pyobs_weather/frontend/static/frontend/dist /weather/pyobs_weather/frontend/static/frontend/dist

CMD uv run gunicorn --bind 0.0.0.0:8002 --workers=6 --threads=3 --worker-class=gthread pyobs_weather.wsgi
