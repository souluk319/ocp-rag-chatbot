"""RAG 챗봇 평가 질문 세트 + 자동 테스트

사용법:
    python scripts/eval_questions.py              # 전체 평가 실행
    python scripts/eval_questions.py --dry-run     # 질문 목록만 출력
    python scripts/eval_questions.py --category troubleshooting  # 카테고리별
"""
import asyncio
import sys
import os
import json
import time
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.embedding import EmbeddingEngine
from src.vectorstore import IVFIndex
from src.retriever import Retriever
from src.config import INDEX_DIR, EMBEDDING_DIM, TOP_K

# ============================================================
# 평가 질문 세트 (카테고리별)
# ============================================================
EVAL_QUESTIONS = [
    # === 기본 개념 ===
    {"q": "쿠버네티스가 뭐야?", "category": "concept", "expected_source": "k8s"},
    {"q": "오픈시프트란 무엇인가?", "category": "concept", "expected_source": "ocp"},
    {"q": "Pod란 무엇이고 왜 필요한가?", "category": "concept", "expected_source": "k8s"},
    {"q": "Deployment와 StatefulSet의 차이는?", "category": "concept", "expected_source": "k8s"},
    {"q": "DaemonSet은 언제 사용해?", "category": "concept", "expected_source": "k8s"},
    {"q": "Service의 종류와 차이점은?", "category": "concept", "expected_source": "k8s"},
    {"q": "ClusterIP, NodePort, LoadBalancer 차이", "category": "concept", "expected_source": "k8s"},
    {"q": "Ingress와 Route의 차이는?", "category": "concept", "expected_source": "ocp"},
    {"q": "ConfigMap이란 무엇이고 어떻게 사용해?", "category": "concept", "expected_source": "k8s"},
    {"q": "Kubernetes Secret이란 무엇인가?", "category": "concept", "expected_source": "k8s"},
    {"q": "PV와 PVC의 차이는?", "category": "concept", "expected_source": "k8s"},
    {"q": "Namespace와 Project의 차이는?", "category": "concept", "expected_source": "ocp"},
    {"q": "OCP에서 Operator란 무엇인가?", "category": "concept", "expected_source": "ocp"},
    {"q": "RBAC이란 무엇이고 왜 필요해?", "category": "concept", "expected_source": "k8s"},
    {"q": "SCC(Security Context Constraints)란?", "category": "concept", "expected_source": "ocp"},
    {"q": "etcd가 뭐야? 왜 중요해?", "category": "concept", "expected_source": "ocp"},
    {"q": "컨테이너와 Pod의 관계는?", "category": "concept", "expected_source": "k8s"},
    {"q": "ReplicaSet의 역할은?", "category": "concept", "expected_source": "k8s"},
    {"q": "Label과 Selector는 어떻게 동작해?", "category": "concept", "expected_source": "k8s"},
    {"q": "Helm이란 무엇이고 왜 쓰나?", "category": "concept", "expected_source": "ocp"},

    # === 실무 절차 ===
    {"q": "Pod를 생성하는 방법은?", "category": "procedure", "expected_source": "k8s"},
    {"q": "Deployment를 롤백하는 방법은?", "category": "procedure", "expected_source": "k8s"},
    {"q": "OCP에서 프로젝트를 생성하는 방법은?", "category": "procedure", "expected_source": "ocp"},
    {"q": "ConfigMap을 Pod에 마운트하는 방법", "category": "procedure", "expected_source": "k8s"},
    {"q": "Secret을 환경변수로 주입하는 방법", "category": "procedure", "expected_source": "k8s"},
    {"q": "HPA를 설정하는 방법은?", "category": "procedure", "expected_source": "k8s"},
    {"q": "ResourceQuota를 설정하는 YAML 예시", "category": "procedure", "expected_source": "k8s"},
    {"q": "LimitRange 설정 방법", "category": "procedure", "expected_source": "k8s"},
    {"q": "NetworkPolicy로 트래픽 제한하는 방법", "category": "procedure", "expected_source": "k8s"},
    {"q": "TLS Route를 생성하는 방법", "category": "procedure", "expected_source": "ocp"},
    {"q": "이미지 Pull Secret을 설정하는 방법", "category": "procedure", "expected_source": "k8s"},
    {"q": "노드에 Taint와 Toleration 설정하는 방법", "category": "procedure", "expected_source": "ocp"},
    {"q": "PVC를 생성하고 Pod에 연결하는 방법", "category": "procedure", "expected_source": "k8s"},
    {"q": "Liveness Probe와 Readiness Probe 설정 방법", "category": "procedure", "expected_source": "k8s"},
    {"q": "OCP에서 S2I 빌드하는 방법", "category": "procedure", "expected_source": "ocp"},

    # === 트러블슈팅 ===
    {"q": "Pod가 CrashLoopBackOff일 때 해결방법은?", "category": "troubleshooting", "expected_source": "any"},
    {"q": "Pod가 Pending 상태에서 안 넘어가요", "category": "troubleshooting", "expected_source": "any"},
    {"q": "ImagePullBackOff 에러 해결방법", "category": "troubleshooting", "expected_source": "any"},
    {"q": "OOMKilled가 발생하면 어떻게 해?", "category": "troubleshooting", "expected_source": "any"},
    {"q": "Pod 로그를 확인하는 방법은?", "category": "troubleshooting", "expected_source": "any"},
    {"q": "이전 컨테이너 로그 보는 방법", "category": "troubleshooting", "expected_source": "any"},
    {"q": "노드가 NotReady 상태일 때 대응방법", "category": "troubleshooting", "expected_source": "ocp"},
    {"q": "PVC가 Pending에서 안 바뀌어요", "category": "troubleshooting", "expected_source": "any"},
    {"q": "Service에 연결이 안 될 때 확인사항", "category": "troubleshooting", "expected_source": "any"},
    {"q": "DNS 이름으로 Pod 간 통신이 안 돼요", "category": "troubleshooting", "expected_source": "any"},
    {"q": "Pod 이벤트를 확인하는 명령어는?", "category": "troubleshooting", "expected_source": "any"},
    {"q": "컨테이너가 계속 재시작되는 원인은?", "category": "troubleshooting", "expected_source": "any"},
    {"q": "oc debug 사용법", "category": "troubleshooting", "expected_source": "ocp"},
    {"q": "must-gather로 클러스터 정보 수집하는 방법", "category": "troubleshooting", "expected_source": "ocp"},

    # === 운영/관리 ===
    {"q": "OCP 클러스터 업그레이드 절차는?", "category": "operations", "expected_source": "ocp"},
    {"q": "etcd 백업하는 방법", "category": "operations", "expected_source": "ocp"},
    {"q": "etcd 복구 절차", "category": "operations", "expected_source": "ocp"},
    {"q": "노드를 drain하는 방법과 주의사항", "category": "operations", "expected_source": "ocp"},
    {"q": "노드를 cordon/uncordon하는 방법", "category": "operations", "expected_source": "ocp"},
    {"q": "클러스터 리소스 사용량 확인 방법", "category": "operations", "expected_source": "any"},
    {"q": "oc adm top nodes 명령어 설명", "category": "operations", "expected_source": "ocp"},
    {"q": "로그를 중앙에서 수집하는 방법", "category": "operations", "expected_source": "ocp"},
    {"q": "Prometheus로 모니터링하는 방법", "category": "operations", "expected_source": "ocp"},
    {"q": "Alert 규칙을 설정하는 방법", "category": "operations", "expected_source": "ocp"},

    # === CI/CD & 배포 ===
    {"q": "Blue-Green 배포와 Canary 배포의 차이", "category": "cicd", "expected_source": "ocp"},
    {"q": "Rolling Update 전략 설명", "category": "cicd", "expected_source": "k8s"},
    {"q": "Tekton 파이프라인이란?", "category": "cicd", "expected_source": "ocp"},
    {"q": "ArgoCD로 GitOps 하는 방법", "category": "cicd", "expected_source": "ocp"},
    {"q": "ImageStream이란 무엇인가?", "category": "cicd", "expected_source": "ocp"},

    # === 보안 ===
    {"q": "Pod Security Standards 종류는?", "category": "security", "expected_source": "ocp"},
    {"q": "최소 권한 원칙으로 RBAC 설정하는 방법", "category": "security", "expected_source": "any"},
    {"q": "이미지 스캐닝이란?", "category": "security", "expected_source": "ocp"},
    {"q": "감사(Audit) 로그 확인 방법", "category": "security", "expected_source": "ocp"},

    # === 명령어 ===
    {"q": "자주 쓰는 oc 명령어 모음", "category": "commands", "expected_source": "ocp"},
    {"q": "kubectl get pods 옵션들 설명", "category": "commands", "expected_source": "k8s"},
    {"q": "oc login 하는 방법", "category": "commands", "expected_source": "ocp"},
    {"q": "kubectl apply와 create의 차이", "category": "commands", "expected_source": "k8s"},
]

# 실패 판정 키워드
FAIL_KEYWORDS = [
    "찾지 못했습니다",
    "찾을 수 없",
    "해당 정보를 찾",
    "관련 문서를 찾",
    "포함되어 있지 않",
    "제공된 문서에서",
    "공식 문서를 참조",
    "관련 공식 문서를 참",
    "문서에 포함되어 있지",
    "정보가 부족",
]


def check_fail(answer: str) -> bool:
    """답변이 '못 찾겠다' 류인지 판별"""
    answer_lower = answer.lower()
    for kw in FAIL_KEYWORDS:
        if kw in answer_lower:
            return True
    return False


async def run_eval(questions: list[dict], dry_run: bool = False):
    """평가 실행"""
    if dry_run:
        print(f"\n총 {len(questions)}개 질문:\n")
        for i, q in enumerate(questions, 1):
            print(f"  [{i:2d}] [{q['category']:15s}] {q['q']}")
        return

    # 컴포넌트 로드
    print("컴포넌트 로딩 중...")
    engine = EmbeddingEngine()
    index = IVFIndex.load(INDEX_DIR)
    retriever = Retriever(index=index, embedding_engine=engine)
    if index.documents:
        retriever.bm25.index_corpus(index.documents)
    print(f"  인덱스: {index.stats()['total_vectors']}개 벡터")
    print(f"  BM25: {len(index.documents)}개 문서\n")

    results = []
    total = len(questions)

    for i, q_item in enumerate(questions, 1):
        query = q_item["q"]
        category = q_item["category"]

        # 검색만 수행 (LLM 호출 안 함 — 검색 품질만 평가)
        start = time.time()
        ranked = retriever.retrieve(query, top_k=5)
        elapsed = time.time() - start

        if ranked:
            top_score = ranked[0].score
            top_source = ranked[0].metadata.get("source", "?")
            top_text = ranked[0].text[:100]
            sources = [r.metadata.get("source", "?") for r in ranked]
        else:
            top_score = 0
            top_source = "NONE"
            top_text = ""
            sources = []

        # 점수 기준 판정
        if top_score >= 0.6:
            status = "✅ PASS"
        elif top_score >= 0.4:
            status = "⚠️ WEAK"
        else:
            status = "❌ FAIL"

        results.append({
            "query": query,
            "category": category,
            "status": status,
            "top_score": top_score,
            "top_source": top_source,
            "sources": sources,
            "time_ms": int(elapsed * 1000),
        })

        # 진행률 표시
        icon = status.split()[0]
        print(f"  [{i:2d}/{total}] {icon} {top_score:.3f} | {category:15s} | {query[:40]:40s} | {top_source[:35]}")

    # ============================================================
    # 결과 요약
    # ============================================================
    print(f"\n{'='*80}")
    print("평가 결과 요약")
    print(f"{'='*80}")

    pass_count = sum(1 for r in results if "PASS" in r["status"])
    weak_count = sum(1 for r in results if "WEAK" in r["status"])
    fail_count = sum(1 for r in results if "FAIL" in r["status"])

    print(f"\n  ✅ PASS (≥0.6): {pass_count}/{total}")
    print(f"  ⚠️  WEAK (0.4~0.6): {weak_count}/{total}")
    print(f"  ❌ FAIL (<0.4): {fail_count}/{total}")
    print(f"  검색 정확도: {pass_count/total*100:.1f}%")

    # 카테고리별 요약
    categories = sorted(set(r["category"] for r in results))
    print(f"\n카테고리별:")
    for cat in categories:
        cat_results = [r for r in results if r["category"] == cat]
        cat_pass = sum(1 for r in cat_results if "PASS" in r["status"])
        cat_avg = sum(r["top_score"] for r in cat_results) / len(cat_results)
        print(f"  {cat:15s}: {cat_pass}/{len(cat_results)} pass, avg score {cat_avg:.3f}")

    # 실패/약한 질문 상세
    problems = [r for r in results if "FAIL" in r["status"] or "WEAK" in r["status"]]
    if problems:
        print(f"\n{'='*80}")
        print(f"보강 필요 목록 ({len(problems)}개)")
        print(f"{'='*80}")
        for r in sorted(problems, key=lambda x: x["top_score"]):
            print(f"  {r['status']} score={r['top_score']:.3f} | {r['query']}")
            print(f"         top_source: {r['top_source']}")

    # JSON 저장
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "eval_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n상세 결과 저장: {output_path}")


async def main():
    parser = argparse.ArgumentParser(description="RAG 챗봇 평가")
    parser.add_argument("--dry-run", action="store_true", help="질문 목록만 출력")
    parser.add_argument("--category", type=str, default=None, help="특정 카테고리만 (concept, procedure, troubleshooting, operations, cicd, security, commands)")
    args = parser.parse_args()

    questions = EVAL_QUESTIONS
    if args.category:
        questions = [q for q in questions if q["category"] == args.category]

    print(f"\n{'='*80}")
    print(f"OCP RAG Chatbot - Search Quality Eval ({len(questions)} questions)")
    print(f"{'='*80}")

    await run_eval(questions, dry_run=args.dry_run)


if __name__ == "__main__":
    asyncio.run(main())
