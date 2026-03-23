"""전역 설정 관리"""
import os
from dotenv import load_dotenv

load_dotenv()

# LLM 설정
LLM_ENDPOINT = os.getenv("LLM_ENDPOINT", "http://localhost:8080/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "Qwen/Qwen3.5-9B")
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2048"))
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))

# LLM 엔드포인트 목록 (UI에서 선택 가능)
LLM_ENDPOINTS = {
    "company": {
        "name": os.getenv("LLM_EP_COMPANY_NAME", "회사 서버"),
        "url":  os.getenv("LLM_EP_COMPANY_URL", "http://localhost:8080/v1"),
        "model": os.getenv("LLM_EP_COMPANY_MODEL", "Qwen/Qwen3.5-9B"),
    },
    "macmini": {
        "name": os.getenv("LLM_EP_MACMINI_NAME", "Mac Mini"),
        "url":  os.getenv("LLM_EP_MACMINI_URL", "http://localhost:8080/v1"),
        "model": os.getenv("LLM_EP_MACMINI_MODEL", "Qwen/Qwen3.5-9B"),
    },
    "rtx": {
        "name": os.getenv("LLM_EP_RTX_NAME", "RTX Desktop"),
        "url":  os.getenv("LLM_EP_RTX_URL", "http://localhost:8080/v1"),
        "model": os.getenv("LLM_EP_RTX_MODEL", "Qwen/Qwen3.5-9B"),
    },
}

# Embedding 설정
# 처음에 all-MiniLM-L6-v2 썼는데 한국어 질의 → 영어 문서 매칭이 너무 약해서
# multilingual 모델로 교체. 차원(384)은 같아서 인덱스 구조 변경 없음.
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "384"))

# Chunking 설정
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "128"))

# Vector Index 설정
INDEX_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "index")
TOP_K = int(os.getenv("TOP_K", "5"))
IVF_N_CLUSTERS = int(os.getenv("IVF_N_CLUSTERS", "16"))
# n_probe: 검색 시 탐색할 클러스터 수. 문서 5400개에서 3은 recall 부족 → 6으로 상향
# 14373벡터에서 IVF 클러스터 누락 방지 → 16 전수탐색 (26ms로 속도 영향 없음)
IVF_N_PROBE = int(os.getenv("IVF_N_PROBE", "16"))

# Session 설정
MAX_HISTORY_TURNS = int(os.getenv("MAX_HISTORY_TURNS", "10"))
SESSION_TTL_SECONDS = int(os.getenv("SESSION_TTL_SECONDS", "3600"))

# Cache 설정
# 0.92에서 오탐 발생해서 0.95로 올림 (멀티턴 테스트에서 "모니터링"과 "리소스 제한"이 캐시 히트됨)
CACHE_SIMILARITY_THRESHOLD = float(os.getenv("CACHE_SIMILARITY_THRESHOLD", "0.95"))
CACHE_MAX_SIZE = int(os.getenv("CACHE_MAX_SIZE", "200"))

# 데이터 경로
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
DATA_PRIVATE_RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
DATA_SANITIZED_DIR = os.path.join(PROJECT_ROOT, "data", "sanitized_raw")
# 챗봇과 인덱서는 비공개 raw가 아니라 정제된 최종본만 사용한다.
DATA_CORPUS_DIR = os.getenv("DATA_CORPUS_DIR", DATA_SANITIZED_DIR)

# 서버 설정
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
