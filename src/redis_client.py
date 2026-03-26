"""Redis 연결 헬퍼. REDIS_URL 미설정 또는 연결 실패 시 None 반환 (graceful fallback)."""
import logging
import os

logger = logging.getLogger(__name__)

_client = None
_tried = False


def get_redis():
    """동기 Redis 클라이언트 반환. 연결 불가 시 None.

    첫 호출 시 연결을 시도하고 결과를 캐싱한다.
    REDIS_URL 환경 변수가 없으면 즉시 None 반환 (인메모리 모드).
    """
    global _client, _tried
    if _tried:
        return _client

    _tried = True
    redis_url = os.getenv("REDIS_URL", "")
    if not redis_url:
        return None

    try:
        import redis as redis_lib
        client = redis_lib.from_url(
            redis_url,
            decode_responses=False,
            socket_connect_timeout=3,
            socket_timeout=5,
        )
        client.ping()
        _client = client
        logger.info("Redis 연결 성공: %s", redis_url)
    except Exception as e:
        logger.warning("Redis 연결 실패 (%s). 인메모리 모드로 동작합니다.", e)

    return _client


def reset_for_testing():
    """테스트 전용 — 연결 상태 초기화"""
    global _client, _tried
    _client = None
    _tried = False
