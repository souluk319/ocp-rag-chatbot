"""Project configuration."""
import os
from dotenv import load_dotenv

load_dotenv()


def _env_flag(name: str, default: str = "0") -> bool:
    value = os.getenv(name, default).strip().lower()
    return value in {"1", "true", "yes", "on"}


# Submission / demo safety switches.
# The default is locked down for grading and public ngrok usage.
SUBMISSION_MODE = _env_flag("SUBMISSION_MODE", "1")
EXPOSE_LLM_ENDPOINT_SWITCHER = _env_flag(
    "EXPOSE_LLM_ENDPOINT_SWITCHER",
    "0" if SUBMISSION_MODE else "1",
)
EXPOSE_DEBUG_ENDPOINTS = (not SUBMISSION_MODE) and _env_flag("EXPOSE_DEBUG_ENDPOINTS", "1")

# Lock the project to the allowed grading model.
LOCKED_LLM_MODEL = "Qwen/Qwen3.5-9B"
ALLOWED_LLM_MODELS = (LOCKED_LLM_MODEL,)

# LLM settings
LLM_ENDPOINT = os.getenv("LLM_ENDPOINT", "http://localhost:8080/v1")
LLM_MODEL = LOCKED_LLM_MODEL
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2048"))
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))

# LLM endpoints are kept for internal routing, but the model is locked.
LLM_ENDPOINTS = {
    "company": {
        "name": os.getenv("LLM_EP_COMPANY_NAME", "Company Server"),
        "url": os.getenv("LLM_EP_COMPANY_URL", "http://localhost:8080/v1"),
        "model": LOCKED_LLM_MODEL,
    },
    "macmini": {
        "name": os.getenv("LLM_EP_MACMINI_NAME", "Mac Mini"),
        "url": os.getenv("LLM_EP_MACMINI_URL", "http://localhost:8080/v1"),
        "model": LOCKED_LLM_MODEL,
    },
    "rtx": {
        "name": os.getenv("LLM_EP_RTX_NAME", "RTX Desktop"),
        "url": os.getenv("LLM_EP_RTX_URL", "http://localhost:8080/v1"),
        "model": LOCKED_LLM_MODEL,
    },
}

PRIMARY_LLM_ENDPOINT_KEY = os.getenv("PRIMARY_LLM_ENDPOINT_KEY", "company")

# Embedding settings
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "384"))

# Chunking settings
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "128"))

# Vector index settings
INDEX_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "index")
TOP_K = int(os.getenv("TOP_K", "5"))
IVF_N_CLUSTERS = int(os.getenv("IVF_N_CLUSTERS", "16"))
IVF_N_PROBE = int(os.getenv("IVF_N_PROBE", "16"))

# Session settings
MAX_HISTORY_TURNS = int(os.getenv("MAX_HISTORY_TURNS", "10"))
SESSION_TTL_SECONDS = int(os.getenv("SESSION_TTL_SECONDS", "3600"))

# Cache settings
CACHE_SIMILARITY_THRESHOLD = float(os.getenv("CACHE_SIMILARITY_THRESHOLD", "0.95"))
CACHE_MAX_SIZE = int(os.getenv("CACHE_MAX_SIZE", "200"))

# Data paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
DATA_PRIVATE_RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
DATA_SANITIZED_DIR = os.path.join(PROJECT_ROOT, "data", "sanitized_raw")
DATA_CORPUS_DIR = os.getenv("DATA_CORPUS_DIR", DATA_SANITIZED_DIR)

# Server settings
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
