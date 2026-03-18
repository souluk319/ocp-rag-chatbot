"""멀티턴 대화 테스트 스크립트"""
import httpx
import json
import sys

API = "http://localhost:8000/api/chat"

queries = [
    "OCP에서 Pod란 무엇인가요?",
    "그러면 그걸 모니터링하는 방법은?",        # 대명사 "그걸"
    "리소스 제한은 어떻게 설정해?",              # 독립 질문
    "그거 YAML 예시 보여줘",                    # 대명사 "그거"
    "더 알려줘",                                # 극단적 생략
    "ConfigMap과 Secret 차이도 알려줘",          # 주제 전환
]

session_id = None

for i, q in enumerate(queries, 1):
    print(f"\n{'='*60}")
    print(f"Turn {i}: {q}")
    print('='*60)

    payload = {"query": q}
    if session_id:
        payload["session_id"] = session_id

    try:
        resp = httpx.post(API, json=payload, timeout=180.0)
        data = resp.json()

        session_id = data.get("session_id", session_id)
        rewritten = data.get("rewritten_query", "-")
        cached = data.get("cached", False)
        answer = data.get("answer", "")
        sources = data.get("sources", [])

        print(f"  Session: {session_id}")
        print(f"  Rewritten: {rewritten}")
        print(f"  Cached: {cached}")
        print(f"  Sources: {[s['source'] for s in sources[:3]]}")
        print(f"  Answer (preview): {answer[:250]}...")

    except Exception as e:
        print(f"  ERROR: {e}")

print(f"\n{'='*60}")
print(f"테스트 완료: {len(queries)}턴 멀티턴 대화")
print(f"최종 세션 ID: {session_id}")
