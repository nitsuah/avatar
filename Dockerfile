# syntax=docker/dockerfile:1

FROM python:3.11-slim-bookworm AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY config/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ---- test stage ----
FROM base AS test
ENV PYTHONPATH=/app
CMD ["pytest", "tests/", "-v", "--tb=short"]

# ---- notebook stage ----
FROM base AS notebook
RUN useradd -m appuser
USER appuser
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8888/ || exit 1
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser"]