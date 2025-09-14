FROM python:3.13-slim

RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        git ca-certificates \
        build-essential pkg-config \
        # optional but commonly needed:
        libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /recsys-recommender

ENV RUSTUP_HOME=/root/.cache/rustup
ENV CARGO_HOME=/root/.cache/cargo

RUN --mount=type=cache,target=/root/.cache/rustup \
    --mount=type=cache,target=/root/.cache/cargo \
    --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-dev --compile-bytecode

COPY app ./app
COPY gunicorn.conf.py ./gunicorn.conf.py

EXPOSE 8000
ENV PORT=8000

CMD ["/recsys-recommender/.venv/bin/gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-c", "gunicorn.conf.py", "app.main:app"]
