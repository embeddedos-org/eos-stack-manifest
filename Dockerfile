# ═══════════════════════════════════════════════════════════
# ebuild/eFab Dockerfile — Python build toolchain
# ═══════════════════════════════════════════════════════════
FROM python:3.12-slim AS base
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    make \
    git \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements*.txt ./
RUN pip install --no-cache-dir -r requirements.txt 2>/dev/null || true
COPY . .
RUN pip install --no-cache-dir -e . 2>/dev/null || true

FROM base AS test-runner
RUN pip install --no-cache-dir pytest pytest-cov
CMD ["python3", "-m", "pytest", "tests/", "-v", "--tb=short"]

FROM base AS production
CMD ["python3", "-m", "ebuild"]
