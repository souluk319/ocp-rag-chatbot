# ── 빌드 스테이지 ────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# C 확장 빌드에 필요한 최소 패키지
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── 런타임 스테이지 ───────────────────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# 빌드 스테이지 패키지만 복사 (빌드툴 제외)
COPY --from=builder /install /usr/local

# 소스 코드
COPY src/      ./src/
COPY frontend/ ./frontend/
COPY scripts/  ./scripts/

# HuggingFace 모델 캐시 경로 (볼륨 마운트 대상)
ENV HF_HOME=/app/.cache/huggingface
ENV TRANSFORMERS_CACHE=/app/.cache/huggingface

# 데이터 디렉터리는 볼륨으로 마운트 — 컨테이너 안에 미리 생성만
RUN mkdir -p /app/data/index /app/data/sanitized_raw /app/.cache/huggingface

EXPOSE 8000

# 프로세스를 PID 1로 실행 (올바른 시그널 처리)
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
