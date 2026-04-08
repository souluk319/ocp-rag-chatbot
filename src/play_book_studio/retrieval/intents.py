from __future__ import annotations

# retrieval 질문 의도 판별과 관련 regex/heuristic 모음.

import re

OCP_RE = re.compile(r"(?<![a-z0-9])ocp(?![a-z0-9])", re.IGNORECASE)
OPENSHIFT_RE = re.compile(r"(오픈시프트|openshift)", re.IGNORECASE)
KUBERNETES_RE = re.compile(r"(쿠버네티스|kubernetes)", re.IGNORECASE)
COMPARE_RE = re.compile(r"(차이|다른 점|비교|vs|versus|유사점)", re.IGNORECASE)
ARCHITECTURE_RE = re.compile(r"(아키텍처|architecture)", re.IGNORECASE)
LOGGING_RE = re.compile(r"(로그|로깅|logging)", re.IGNORECASE)
AUDIT_RE = re.compile(r"(감사|audit)", re.IGNORECASE)
EVENT_RE = re.compile(r"(이벤트|event)", re.IGNORECASE)
APP_RE = re.compile(r"(애플리케이션|application|pod|컨테이너|container)", re.IGNORECASE)
POD_PENDING_RE = re.compile(r"(pod|파드).*(pending|펜딩)|(pending|펜딩)", re.IGNORECASE)
CRASH_LOOP_RE = re.compile(r"(crashloopbackoff|crash loop backoff|크래시루프백오프)", re.IGNORECASE)
POD_LIFECYCLE_RE = re.compile(
    r"(pod lifecycle|pod 라이프사이클|파드 라이프사이클|pod 생명주기|파드 생명주기|lifecycle)",
    re.IGNORECASE,
)
OC_LOGIN_RE = re.compile(r"\boc\s+login\b|(로그인).*(\boc\b)", re.IGNORECASE)
INFRA_RE = re.compile(r"(인프라|infra|노드|node|컨트롤 플레인|control plane)", re.IGNORECASE)
MONITORING_RE = re.compile(r"(모니터링|monitoring)", re.IGNORECASE)
SECURITY_RE = re.compile(r"(보안|security)", re.IGNORECASE)
AUTH_RE = re.compile(r"(인증|authentication)", re.IGNORECASE)
AUTHZ_RE = re.compile(r"(권한|authorization)", re.IGNORECASE)
UPDATE_RE = re.compile(r"(업데이트|upgrade|update|업그레이드)", re.IGNORECASE)
CERT_RE = re.compile(r"(인증서|certificate|certificates|cert)", re.IGNORECASE)
EXPIRY_RE = re.compile(r"(만료|만료일|만료 상태|expire|expiry|expiration|남았)", re.IGNORECASE)
DEPLOYMENT_RE = re.compile(r"(deployment(?!config)|deployments|디플로이먼트|배포)", re.IGNORECASE)
DEPLOYMENTCONFIG_RE = re.compile(r"(deploymentconfig|\bdc\b|디플로이먼트컨피그)", re.IGNORECASE)
SCALE_RE = re.compile(r"(스케일|scale|늘리|줄이|변경|조정)", re.IGNORECASE)
REPLICA_RE = re.compile(r"(복제본|replica|replicas)", re.IGNORECASE)
RBAC_RE = re.compile(
    r"(\brbac\b|역할 기반 액세스 제어|rolebinding|clusterrolebinding|clusterrole|역할 바인딩|role binding)",
    re.IGNORECASE,
)
PROJECT_SCOPE_RE = re.compile(r"(프로젝트|project|네임스페이스|namespace)", re.IGNORECASE)
ROLE_ASSIGN_RE = re.compile(
    r"(주고 싶|주려|부여|할당|추가|설정|바인딩|묶|grant|assign|bind)",
    re.IGNORECASE,
)
ROLE_API_STYLE_RE = re.compile(r"(api|yaml|manifest|json|spec|필드|curl)", re.IGNORECASE)
USER_SUBJECT_RE = re.compile(r"(사용자|유저|작업자|계정|그룹|serviceaccount|서비스 계정)", re.IGNORECASE)
ADMIN_ROLE_RE = re.compile(r"(관리자|\badmin\b)", re.IGNORECASE)
EDIT_ROLE_RE = re.compile(r"(편집|\bedit\b)", re.IGNORECASE)
VIEW_ROLE_RE = re.compile(r"(읽기 전용|보기|\bview\b)", re.IGNORECASE)
CLUSTER_ADMIN_RE = re.compile(r"\bcluster-admin\b", re.IGNORECASE)
MCO_RE = re.compile(
    r"(machine config operator|mco(?:가|는|를|란|와|과)?|머신\s*컨피그\s*오퍼레이터|머신\s*구성\s*오퍼레이터)",
    re.IGNORECASE,
)
DISCONNECTED_RE = re.compile(r"(연결이 없는 환경|분리망|disconnect)", re.IGNORECASE)
ETCD_RE = re.compile(r"etcd", re.IGNORECASE)
BACKUP_RE = re.compile(r"(백업|backup)", re.IGNORECASE)
RESTORE_RE = re.compile(r"(복구|복원|restore)", re.IGNORECASE)
NODE_RE = re.compile(r"(노드|node|worker)", re.IGNORECASE)
DRAIN_RE = re.compile(r"(drain|비워|비우|evacuate|점검 때문에 비워)", re.IGNORECASE)
TOP_RE = re.compile(r"(\btop\b|사용량|cpu|메모리|memory)", re.IGNORECASE)
HOSTED_CONTROL_PLANE_RE = re.compile(
    r"(hosted control plane|hosted cluster|호스팅된 컨트롤 플레인|호스트된 컨트롤 플레인|hypershift|oadp|velero)",
    re.IGNORECASE,
)
PROJECT_TERMINATING_RE = re.compile(
    r"(프로젝트|project|namespace|네임스페이스).*(삭제|지웠|지우|terminating|종료 중|안 없어|안 없어지|안 지워|안 지워지)",
    re.IGNORECASE,
)
FINALIZER_RE = re.compile(
    r"(finalizer|finalizers|metadata\.finalizers|강제 제거|강제로 제거|finalizer 제거)",
    re.IGNORECASE,
)
REMAINING_RESOURCE_RE = re.compile(
    r"(걸려 있는 리소스|남아 있는 리소스|remaining resource|resource resolving|error resolving resource|crd|custom resource|리소스 에러)",
    re.IGNORECASE,
)
OPERATOR_RE = re.compile(
    r"(오퍼레이터|operator(?:가|는|를|란|와|과)?|\boperator\b)",
    re.IGNORECASE,
)
DOC_LOCATOR_RE = re.compile(
    r"(문서|가이드|어디서|어디 있어|어디를|찾아|찾을|봐야|보려면|보고 싶|참고할)",
    re.IGNORECASE,
)
SECURITY_SCOPE_RE = re.compile(
    r"(컴플라이언스|compliance|감사|audit|인증|authentication|권한|authorization|rbac|네트워크|network|tls|certificate|cert|암호화|egress|ingress)",
    re.IGNORECASE,
)
EXPLAINER_RE = re.compile(
    r"(설명해줘|설명해 줘|처음 설명|처음부터 설명|개념 설명|뭐야\??|무엇인가\??|무슨 역할|왜 중요|차이가 뭐야\??|역할이 뭐야\??|뭘 해\??|무엇을 해\??|what does .* do|요약해줘|요약해 줘|요약해봐|요약해 봐|정리해줘|정리해 줘|세줄|3줄|한줄|짧게)",
    re.IGNORECASE,
)
GENERIC_INTRO_RE = re.compile(
    r"(오픈시프트|openshift).*(뭐야|무엇|소개|개요|아키텍처|architecture)|"
    r"(오픈시프트|openshift).*(요약|정리|세줄|3줄|한줄|짧게)|"
    r"(쿠버네티스|kubernetes).*(오픈시프트|openshift).*(차이|다른 점)",
    re.IGNORECASE,
)
COMPARE_DECOMPOSE_RE = re.compile(
    r"(?P<left>.+?)(?:\s*(?:vs\.?|versus|와|과|랑)\s*)(?P<right>.+?)(?:\s*(?:의)?\s*(?:차이|차이점|비교|다른 점).*)$",
    re.IGNORECASE,
)
ROUTE_TIMEOUT_RE = re.compile(r"(route|루트).*(시간|timeout|타임아웃|늘리|줄이|변경|조정)", re.IGNORECASE)
NODE_NOTREADY_RE = re.compile(r"(node|노드|worker|워커).*(notready|안돼|왜그래|상태|죽었|끊겼)", re.IGNORECASE)
CONJUNCTION_SPLIT_RE = re.compile(r"\s*(?:그리고|또한|및|and then|and also|and)\s*", re.IGNORECASE)
GENERIC_CONTEXT_TOPIC_RE = re.compile(
    r"(운영 설정 변경|복구 절차 검토|설정 변경|설정 검토|운영 설정|복구 절차|절차 검토|일반 설정)",
    re.IGNORECASE,
)
MACHINE_CONFIG_REBOOT_RE = re.compile(
    r"((machine\s*config(?:uration)?|머신\s*(?:구성|설정)|mco).*(재부팅|reboot|롤링 재부팅))|((재부팅|reboot).*(machine\s*config(?:uration)?|머신\s*(?:구성|설정)|mco))",
    re.IGNORECASE,
)

# 의도 판별기는 retrieval shaping 여러 곳에서 재사용되므로 파일 상단에 모아 둔다.
# retriever 가중치를 건드리기 전에 이 파일을 위에서 아래로 한 번 읽는 게 좋다.


def has_doc_locator_intent(query: str) -> bool:
    return bool(DOC_LOCATOR_RE.search(query or ""))


def has_update_doc_locator_intent(query: str) -> bool:
    normalized = query or ""
    if not UPDATE_RE.search(normalized):
        return False
    if has_doc_locator_intent(normalized):
        return True
    return any(
        token in normalized
        for token in (
            "릴리스 노트",
            "release notes",
            "업데이트 가이드",
            "업데이트 문서",
            "뭐부터 보면",
            "뭐부터 봐야",
        )
    )


def has_pod_pending_troubleshooting_intent(query: str) -> bool:
    return bool(POD_PENDING_RE.search(query or ""))


def has_backup_restore_intent(query: str) -> bool:
    return bool(BACKUP_RE.search(query or "") or RESTORE_RE.search(query or ""))


def has_hosted_control_plane_signal(query: str) -> bool:
    return bool(HOSTED_CONTROL_PLANE_RE.search(query or ""))


def has_certificate_monitor_intent(query: str) -> bool:
    normalized = query or ""
    return bool(CERT_RE.search(normalized)) and bool(
        EXPIRY_RE.search(normalized)
        or "확인" in normalized
        or "조회" in normalized
        or "모니터" in normalized
        or "monitor" in normalized.lower()
    )


def has_rbac_intent(query: str) -> bool:
    normalized = query or ""
    if RBAC_RE.search(normalized):
        return True
    return bool(AUTHZ_RE.search(normalized)) and bool(
        PROJECT_SCOPE_RE.search(normalized)
        or ROLE_ASSIGN_RE.search(normalized)
        or ADMIN_ROLE_RE.search(normalized)
        or EDIT_ROLE_RE.search(normalized)
        or VIEW_ROLE_RE.search(normalized)
        or CLUSTER_ADMIN_RE.search(normalized)
    )


def has_project_scoped_rbac_intent(query: str) -> bool:
    normalized = query or ""
    return has_rbac_intent(normalized) and bool(PROJECT_SCOPE_RE.search(normalized))


def has_rbac_assignment_intent(query: str) -> bool:
    normalized = query or ""
    return has_rbac_intent(normalized) and bool(
        ROLE_ASSIGN_RE.search(normalized)
        or USER_SUBJECT_RE.search(normalized)
        or ADMIN_ROLE_RE.search(normalized)
        or EDIT_ROLE_RE.search(normalized)
        or VIEW_ROLE_RE.search(normalized)
        or CLUSTER_ADMIN_RE.search(normalized)
    )


def has_deployment_scaling_intent(query: str) -> bool:
    normalized = query or ""
    mentions_scale = bool(SCALE_RE.search(normalized)) or bool(REPLICA_RE.search(normalized))
    if not mentions_scale:
        return False
    if DEPLOYMENTCONFIG_RE.search(normalized):
        return False
    if DEPLOYMENT_RE.search(normalized):
        return True
    lowered = normalized.lower()
    return any(
        token in lowered
        for token in (
            "oc scale deployment",
            "deployment/",
            "deployments.apps/scale",
            "replicas를",
            "복제본 개수",
            "복제본 수",
        )
    )


def has_command_request(query: str) -> bool:
    normalized = query or ""
    return bool(
        re.search(
            r"(명령어|커맨드|cli|oc\s|kubectl\s|yaml|예시|예제로|어떤 명령|뭐라고 쳐|입력하면)",
            normalized,
            re.IGNORECASE,
        )
    )


def is_generic_intro_query(query: str) -> bool:
    lowered = (query or "").lower()
    if GENERIC_INTRO_RE.search(query or ""):
        return True
    has_ocp_topic = "openshift" in lowered or bool(OCP_RE.search(query or ""))
    return has_ocp_topic and bool(
        ARCHITECTURE_RE.search(query or "") or EXPLAINER_RE.search(query or "")
    )


def has_openshift_kubernetes_compare_intent(query: str) -> bool:
    normalized = query or ""
    return bool(OPENSHIFT_RE.search(normalized)) and bool(KUBERNETES_RE.search(normalized)) and bool(
        COMPARE_RE.search(normalized) or "차이를" in normalized or "차이점" in normalized
    )


def is_explainer_query(query: str) -> bool:
    return bool(EXPLAINER_RE.search(query or ""))


def has_pod_lifecycle_concept_intent(query: str) -> bool:
    normalized = query or ""
    return bool(POD_LIFECYCLE_RE.search(normalized)) and bool(is_explainer_query(normalized))


def has_crash_loop_troubleshooting_intent(query: str) -> bool:
    return bool(CRASH_LOOP_RE.search(query or ""))


def has_operator_concept_intent(query: str) -> bool:
    normalized = query or ""
    return (
        bool(OPERATOR_RE.search(normalized))
        and not bool(MCO_RE.search(normalized))
        and bool(
            is_explainer_query(normalized)
            or "뭐 하는" in normalized
            or "뭘 해" in normalized
            or "하는 거야" in normalized
            or "어떤 역할" in normalized
            or "왜 필요" in normalized
            or "왜 중요한" in normalized
            or "예시" in normalized
            or "누가 관리" in normalized
            or "뭘 관리" in normalized
            or "관리해" in normalized
            or (
                has_doc_locator_intent(normalized)
                and any(
                    token in normalized
                    for token in ("처음", "설명", "개념", "기초", "입문")
                )
            )
        )
    )


def has_mco_concept_intent(query: str) -> bool:
    normalized = query or ""
    return bool(MCO_RE.search(normalized)) and bool(
        is_explainer_query(normalized)
        or "뭐 하는" in normalized
        or "뭘 해" in normalized
        or "하는 거야" in normalized
        or "어떤 역할" in normalized
        or "누가 관리" in normalized
        or "뭘 관리" in normalized
        or "건드리면" in normalized
        or "관리해" in normalized
        or (
            has_doc_locator_intent(normalized)
            and any(
                token in normalized
                for token in ("처음", "설명", "개념", "기초", "입문")
            )
        )
    )


def has_machine_config_reboot_intent(query: str) -> bool:
    return bool(MACHINE_CONFIG_REBOOT_RE.search(query or ""))


def has_project_terminating_intent(query: str) -> bool:
    normalized = query or ""
    return bool(PROJECT_TERMINATING_RE.search(normalized))


def has_project_finalizer_intent(query: str) -> bool:
    normalized = query or ""
    return bool(FINALIZER_RE.search(normalized)) or (
        has_project_terminating_intent(normalized)
        and bool(REMAINING_RESOURCE_RE.search(normalized))
    )


def has_node_drain_intent(query: str) -> bool:
    normalized = query or ""
    return bool(NODE_RE.search(normalized)) and bool(DRAIN_RE.search(normalized))


def has_cluster_node_usage_intent(query: str) -> bool:
    normalized = query or ""
    return bool(NODE_RE.search(normalized)) and bool(TOP_RE.search(normalized))


def has_explicit_topic_signal(query: str) -> bool:
    normalized = query or ""
    return any(
        [
            bool(OCP_RE.search(normalized)),
            bool(OPENSHIFT_RE.search(normalized)),
            bool(ETCD_RE.search(normalized)),
            bool(MCO_RE.search(normalized)),
            bool(RBAC_RE.search(normalized)),
            bool(PROJECT_SCOPE_RE.search(normalized)),
            bool(LOGGING_RE.search(normalized)),
            bool(MONITORING_RE.search(normalized)),
            bool(SECURITY_RE.search(normalized)),
            bool(AUTH_RE.search(normalized)),
            bool(AUTHZ_RE.search(normalized)),
            bool(DEPLOYMENT_RE.search(normalized) and (SCALE_RE.search(normalized) or REPLICA_RE.search(normalized))),
            bool(ARCHITECTURE_RE.search(normalized)),
            bool(OPERATOR_RE.search(normalized)),
        ]
    )
