# ==============================================================================
# Institutional Quant Platform
# Production Dockerfile
# ==============================================================================

FROM python:3.12-slim AS builder

LABEL maintainer="Pavan Sai Nekkala"
LABEL application="Institutional Quant Platform"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        git \
        curl \
        libpq-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY requirements.txt .

RUN python -m pip install --upgrade pip setuptools wheel

RUN pip install --prefix=/install -r requirements.txt

# ==============================================================================
# Runtime Image
# ==============================================================================

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    TZ=UTC

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        tini && \
    rm -rf /var/lib/apt/lists/*

RUN groupadd --system quant && \
    useradd --system \
    --gid quant \
    --create-home \
    --home-dir /home/quant \
    quant

WORKDIR /app

COPY --from=builder /install /usr/local

COPY . .

RUN mkdir -p \
    logs \
    reports \
    data \
    artifacts \
    cache \
    tmp

RUN chown -R quant:quant /app

USER quant

EXPOSE 8000

HEALTHCHECK \
    --interval=30s \
    --timeout=10s \
    --start-period=30s \
    --retries=3 \
CMD python -c "import pathlib; pathlib.Path('.').exists()" || exit 1

ENTRYPOINT ["/usr/bin/tini","--"]

CMD ["python","main.py"]