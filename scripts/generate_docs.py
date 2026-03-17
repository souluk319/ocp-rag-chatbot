"""LLM 기반 합성 문서 생성 스크립트

Qwen3.5-9B의 사전학습 지식을 활용하여 RAG에 부족한 주제의
한국어 기술 문서를 자동 생성합니다.

사용법:
    python3 scripts/generate_docs.py              # 전체 생성
    python3 scripts/generate_docs.py --list        # 토픽 목록만 출력
    python3 scripts/generate_docs.py --topic 0,1,2 # 특정 토픽만 생성
"""
import asyncio
import os
import sys
import argparse

# 프로젝트 루트를 path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.llm import LLMClient

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw")

SYSTEM_PROMPT = """당신은 OpenShift Container Platform(OCP)과 Kubernetes 전문가입니다.
신입 엔지니어를 위한 한국어 기술 문서를 작성해야 합니다.

작성 규칙:
1. 한국어로 작성하되, 기술 용어(Pod, Deployment, Service 등)는 영어 그대로 사용
2. 마크다운 형식으로 작성 (제목, 소제목, 불릿, 코드블록, 표 활용)
3. 반드시 다음을 포함:
   - 개념 설명 (왜 필요한지, 어떤 문제를 해결하는지)
   - 핵심 특징 비교 (표 형태)
   - YAML 또는 설정 예시
   - oc / kubectl 명령어 예시
   - 실무 팁 또는 주의사항
4. 정확한 기술 정보만 작성 (추측하지 말 것)
5. 2000자 이상으로 충분히 상세하게 작성"""


# 생성할 토픽 목록
TOPICS = [
    {
        "filename": "ocp-monitoring-ko.md",
        "title": "OCP 모니터링 & 로깅",
        "prompt": """다음 내용을 포함하는 'OCP/Kubernetes 모니터링 & 로깅 가이드' 문서를 작성하세요:

1. 모니터링 개요: 왜 모니터링이 필요한지, 관찰가능성(Observability)의 3가지 축 (메트릭, 로그, 트레이스)
2. Prometheus: 개념, 아키텍처(서버, AlertManager, Exporter), 메트릭 수집 방식, PromQL 기본 쿼리 예시
3. Grafana: 대시보드 개념, Prometheus 데이터 소스 연동
4. OCP 내장 모니터링: openshift-monitoring 네임스페이스, 기본 제공 대시보드
5. 로깅 스택: EFK/ELK (Elasticsearch, Fluentd/Fluent Bit, Kibana) 개요
6. OCP Logging Operator를 통한 로그 수집
7. 알림(Alert) 설정: PrometheusRule, AlertManager 라우팅
8. 실무 명령어: oc adm top, oc get events, 메트릭 확인 명령어""",
    },
    {
        "filename": "ocp-cicd-ko.md",
        "title": "OCP CI/CD & GitOps",
        "prompt": """다음 내용을 포함하는 'OCP CI/CD & GitOps 가이드' 문서를 작성하세요:

1. CI/CD 개요: 지속적 통합/지속적 배포의 개념과 필요성
2. OCP 빌드 전략: Source-to-Image(S2I), Docker Build, Pipeline Build
3. Tekton: 클라우드 네이티브 CI/CD 파이프라인 (Task, Pipeline, PipelineRun 개념)
4. Tekton 파이프라인 YAML 예시 (소스 클론 → 빌드 → 배포)
5. GitOps 개념: 선언적 인프라 관리, Git을 Single Source of Truth로
6. ArgoCD: 개념, OCP와의 통합, Application CRD
7. OpenShift GitOps Operator 설치 및 기본 사용법
8. 이미지 레지스트리: OCP 내장 레지스트리, ImageStream 활용
9. 배포 전략: Rolling, Blue-Green, Canary 배포 비교""",
    },
    {
        "filename": "ocp-network-policy-ko.md",
        "title": "OCP 네트워크 정책 & 서비스 메시",
        "prompt": """다음 내용을 포함하는 'OCP 네트워크 정책 & 서비스 메시 가이드' 문서를 작성하세요:

1. NetworkPolicy 개념: Pod 간 트래픽을 제어하는 방화벽 규칙
2. NetworkPolicy YAML 예시: Ingress 제한, Egress 제한, 네임스페이스 간 통신 제어
3. 기본 정책: deny-all, allow-same-namespace, allow-from-specific-pod
4. OCP SDN vs OVN-Kubernetes: 네트워크 플러그인 비교
5. Service Mesh 개요: 마이크로서비스 통신 관리 (사이드카 패턴)
6. Istio / OpenShift Service Mesh: 트래픽 관리, 보안(mTLS), 관찰가능성
7. Ingress/Route 심화: TLS 종류 (Edge, Passthrough, Re-encrypt), 경로 기반 라우팅
8. DNS 내부 동작: CoreDNS, Service 이름 해석 (service.namespace.svc.cluster.local)""",
    },
    {
        "filename": "ocp-backup-recovery-ko.md",
        "title": "OCP 백업 & 재해복구",
        "prompt": """다음 내용을 포함하는 'OCP 백업 & 재해복구 가이드' 문서를 작성하세요:

1. etcd 백업의 중요성: 클러스터 상태 저장소, 백업 필수인 이유
2. etcd 백업 절차: 스냅샷 생성 명령어, 자동 백업 스크립트
3. etcd 복구 절차: 스냅샷에서 복구하는 단계
4. OADP (OpenShift API for Data Protection): Velero 기반 백업/복구
5. 애플리케이션 백업: PV 데이터 백업, 네임스페이스 단위 백업
6. 재해복구(DR) 전략: RPO/RTO 개념, Active-Passive, Active-Active
7. 클러스터 인증서 갱신: 인증서 만료 시 대응 방법
8. 실무 체크리스트: 정기 백업 주기, 복구 테스트 중요성""",
    },
    {
        "filename": "ocp-helm-ko.md",
        "title": "Helm & 패키지 관리",
        "prompt": """다음 내용을 포함하는 'OCP Helm & 패키지 관리 가이드' 문서를 작성하세요:

1. Helm 개요: Kubernetes 패키지 매니저, Chart/Release/Repository 개념
2. Helm 3 아키텍처: Tiller 제거, 보안 개선
3. Helm Chart 구조: Chart.yaml, values.yaml, templates/ 디렉토리
4. 기본 명령어: helm install, upgrade, rollback, list, uninstall
5. OCP에서 Helm 사용: OperatorHub vs Helm, 사용 시나리오 비교
6. values.yaml 커스터마이징: 환경별 설정 오버라이드
7. Helm Chart 작성: 간단한 Chart 만들기 예시 (Go template 문법)
8. Kustomize: Helm 대안, 패치 기반 설정 관리, OCP에서의 활용""",
    },
    {
        "filename": "ocp-troubleshooting-advanced-ko.md",
        "title": "OCP 고급 트러블슈팅",
        "prompt": """다음 내용을 포함하는 'OCP 고급 트러블슈팅 가이드' 문서를 작성하세요:

1. 노드 트러블슈팅: NotReady 상태 원인, kubelet 로그 확인, 노드 드레인/코든
2. 네트워크 트러블슈팅: Pod 간 통신 불가, DNS 문제, Service 연결 안 됨
3. 스토리지 트러블슈팅: PVC Pending, 볼륨 마운트 실패, 디스크 풀
4. 인증서 문제: 인증서 만료, API 서버 접근 불가
5. 리소스 부족: CPU/Memory throttling, OOMKilled, Eviction 대응
6. etcd 문제: 리더 선출 실패, 데이터 정합성, 성능 저하
7. Operator 문제: CRD 충돌, Operator 업그레이드 실패
8. 디버깅 도구: oc debug, oc adm must-gather, sosreport
9. 실무 디버깅 플로우차트: 증상별 진단 순서""",
    },
    {
        "filename": "ocp-security-advanced-ko.md",
        "title": "OCP 보안 심화",
        "prompt": """다음 내용을 포함하는 'OCP 보안 심화 가이드' 문서를 작성하세요:

1. SCC (Security Context Constraints): OCP 전용 보안 메커니즘, 기본 SCC 종류
2. Pod Security Standards: Privileged, Baseline, Restricted 비교
3. RBAC 심화: Role vs ClusterRole, 최소 권한 원칙, ServiceAccount 보안
4. 네트워크 보안: NetworkPolicy로 마이크로세그멘테이션
5. 이미지 보안: 이미지 스캐닝, 서명 검증, 허용된 레지스트리만 사용
6. Secret 관리: Secret 암호화, Sealed Secrets, HashiCorp Vault 연동 개요
7. 감사(Audit) 로그: API 서버 감사 로그 설정 및 분석
8. 컴플라이언스: CIS 벤치마크, OpenSCAP을 통한 보안 점검""",
    },
    {
        "filename": "ocp-resource-management-ko.md",
        "title": "OCP 리소스 관리 & 최적화",
        "prompt": """다음 내용을 포함하는 'OCP 리소스 관리 & 최적화 가이드' 문서를 작성하세요:

1. ResourceQuota: 네임스페이스별 리소스 할당량 설정, YAML 예시
2. LimitRange: 컨테이너 기본/최대 리소스 설정, YAML 예시
3. PriorityClass: Pod 우선순위 설정, 리소스 경합 시 동작
4. VPA (Vertical Pod Autoscaler): CPU/Memory 자동 조절
5. HPA (Horizontal Pod Autoscaler): 메트릭 기반 Pod 수 자동 조절, YAML 예시
6. Cluster Autoscaler: 노드 수 자동 조절 (클라우드 환경)
7. 용량 계획: 노드 사이징, 워크로드별 리소스 산정 방법
8. 비용 최적화: 리소스 낭비 식별, requests/limits 튜닝 전략
9. oc adm top 명령어로 리소스 사용량 모니터링""",
    },
]


async def generate_doc(llm: LLMClient, topic: dict, index: int, total: int):
    """단일 토픽에 대한 문서 생성"""
    filepath = os.path.join(OUTPUT_DIR, topic["filename"])

    # 이미 존재하면 스킵
    if os.path.exists(filepath) and os.path.getsize(filepath) > 500:
        print(f"  [{index}/{total}] SKIP (exists): {topic['filename']}")
        return True

    print(f"  [{index}/{total}] Generating: {topic['title']}...")

    try:
        content = await llm.generate(SYSTEM_PROMPT, topic["prompt"])

        if not content or len(content) < 200:
            print(f"    -> WARNING: 생성된 내용이 너무 짧습니다 ({len(content) if content else 0}자)")
            return False

        # 제목이 없으면 추가
        if not content.startswith("#"):
            content = f"# {topic['title']}\n\n{content}"

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"    -> OK: {len(content)}자 저장 ({topic['filename']})")
        return True

    except Exception as e:
        print(f"    -> ERROR: {type(e).__name__}: {e}")
        return False


async def main():
    parser = argparse.ArgumentParser(description="LLM 기반 합성 문서 생성")
    parser.add_argument("--list", action="store_true", help="토픽 목록만 출력")
    parser.add_argument("--topic", type=str, default=None,
                        help="생성할 토픽 인덱스 (쉼표 구분, 예: 0,1,2)")
    args = parser.parse_args()

    if args.list:
        print("\n토픽 목록:")
        for i, t in enumerate(TOPICS):
            filepath = os.path.join(OUTPUT_DIR, t["filename"])
            exists = "EXISTS" if os.path.exists(filepath) and os.path.getsize(filepath) > 500 else "NEW"
            print(f"  [{i}] {t['title']:30s} -> {t['filename']:40s} [{exists}]")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 토픽 필터링
    if args.topic:
        indices = [int(x.strip()) for x in args.topic.split(",")]
        topics = [(i, TOPICS[i]) for i in indices if i < len(TOPICS)]
    else:
        topics = list(enumerate(TOPICS))

    total = len(topics)
    print(f"\n{'='*60}")
    print(f"LLM 기반 합성 문서 생성 ({total}개 토픽)")
    print(f"  모델: Qwen3.5-9B")
    print(f"  출력: {OUTPUT_DIR}")
    print(f"{'='*60}\n")

    llm = LLMClient()
    success = 0
    fail = 0

    for idx, (orig_idx, topic) in enumerate(topics, 1):
        result = await generate_doc(llm, topic, idx, total)
        if result:
            success += 1
        else:
            fail += 1

    print(f"\n{'='*60}")
    print(f"문서 생성 완료!")
    print(f"  성공: {success}")
    print(f"  실패: {fail}")
    print(f"\n다음 단계: python3 scripts/build_index.py")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
