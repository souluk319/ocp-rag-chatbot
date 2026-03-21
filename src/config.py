"""전역 설정 관리"""
import os
from dotenv import load_dotenv

load_dotenv()

# LLM 설정
LLM_ENDPOINT = os.getenv("LLM_ENDPOINT", "http://localhost:8080/v1/chat/completions")
LLM_MODEL = os.getenv("LLM_MODEL", "Qwen/Qwen3.5-9B")
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2048"))
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))

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
IVF_N_PROBE = int(os.getenv("IVF_N_PROBE", "6"))

# Session 설정
MAX_HISTORY_TURNS = int(os.getenv("MAX_HISTORY_TURNS", "10"))
SESSION_TTL_SECONDS = int(os.getenv("SESSION_TTL_SECONDS", "3600"))

# Cache 설정
# 0.92에서 오탐 발생해서 0.95로 올림 (멀티턴 테스트에서 "모니터링"과 "리소스 제한"이 캐시 히트됨)
CACHE_SIMILARITY_THRESHOLD = float(os.getenv("CACHE_SIMILARITY_THRESHOLD", "0.95"))
CACHE_MAX_SIZE = int(os.getenv("CACHE_MAX_SIZE", "200"))

# 데이터 경로
DATA_RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw")

# 서버 설정
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
