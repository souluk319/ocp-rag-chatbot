from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
GOLDEN_SET_CSV = REPO_ROOT / "eval" / "benchmarks" / "golden_set_100.csv"
CASES_OUT = REPO_ROOT / "eval" / "benchmarks" / "golden_set_100_cases.jsonl"
RUBRIC_OUT = REPO_ROOT / "eval" / "benchmarks" / "golden_set_100_rubric.json"

STOPWORDS = {
    "무엇인가요",
    "무엇인가",
    "무엇을",
    "어떻게",
    "어디서",
    "어디부터",
    "어느",
    "어떤",
    "무슨",
    "가장",
    "먼저",
    "기준으로",
    "관점에서",
    "정리해",
    "정리해요",
    "정리해줘",
    "해주세요",
    "하나요",
    "되나요",
    "인가요",
    "나요",
    "있나요",
    "있는지",
    "있는",
    "같은",
    "때",
    "시",
    "전에",
    "후에",
    "후",
}

TRAILING_PARTICLES = (
    "입니다",
    "인가요",
    "인가",
    "이요",
    "이에요",
    "예요",
    "이",
    "가",
    "은",
    "는",
    "을",
    "를",
    "와",
    "과",
    "의",
    "로",
    "으로",
)

DOMAIN_KEYWORDS = [
    "OpenShift Container Platform",
    "OpenShift",
    "OCP",
    "control plane",
    "worker",
    "RHCOS",
    "Cluster Operators",
    "OLM",
    "install-config.yaml",
    "must-gather",
    "DiskPressure",
    "ImagePullBackOff",
    "NotReady",
    "PVC",
    "Pending",
    "LDAP",
    "OIDC",
    "PKI",
    "DNS",
    "route",
    "Gateway API",
    "MCP",
    "CNF",
    "y-stream",
    "etcd",
    "oc-mirror",
    "mirror registry",
    "Disconnected",
    "ROSA",
    "OSD",
    "OCM",
    "MicroShift",
    "Lightspeed",
    "HyperShift",
]

SHAPE_RULES = {
    "체크리스트형": ["확인", "점검", "준비", "체크리스트"],
    "단계형": ["먼저", "다음", "이후", "1.", "2."],
    "단계형 안내": ["먼저", "다음", "이후", "1.", "2."],
    "순서형": ["먼저", "다음", "이후", "1.", "2."],
    "비교": ["차이", "비교", "구분", "기준"],
    "비교 설명형": ["차이", "비교", "구분", "기준"],
    "설명형": ["설명", "역할", "의미", "개요"],
    "문서 유도형": ["문서", "가이드", "참고", "확인"],
    "원인 분리형": ["원인", "확인", "점검", "경우"],
    "분기형": ["경우", "이면", "아니면", "분기"],
    "범위 밖 안내": ["범위", "공식", "지원", "내부"],
}

GROUP_CATEGORY_MAP = {
    "core_concept": "other",
    "install_prepare": "install",
    "update_upgrade": "upgrade",
    "disconnected": "troubleshooting",
    "operations": "troubleshooting",
    "out_of_scope": "other",
}

OUT_OF_SCOPE_PRODUCTS = {
    "ROSA": ["ROSA"],
    "OSD": ["OSD"],
    "OCM": ["OCM"],
    "MicroShift": ["MicroShift"],
    "Lightspeed": ["Lightspeed"],
    "HyperShift": ["HyperShift", "hosted control planes", "HCP"],
    "managed service": ["managed service", "매니지드 서비스"],
}

GROUP_REQUIRED_KEYWORD_GROUPS = {
    "core_concept": [["OpenShift", "OCP", "OpenShift Container Platform"]],
    "install_prepare": [["설치", "install"], ["준비", "사전", "확인"]],
    "disconnected": [["폐쇄망", "disconnected"], ["미러", "미러링", "mirror", "oc-mirror"]],
    "update_upgrade": [["업데이트", "update"], ["사전", "확인", "채널", "경로"]],
    "operations": [["운영", "확인", "점검", "원인", "조치"]],
}

INTENT_REQUIRED_KEYWORD_GROUPS = {
    "install_firewall": [["방화벽", "firewall"], ["포트", "port"], ["예외", "allow"]],
    "update_prerequisite": [["업데이트", "update"], ["사전", "확인", "준비"]],
    "disconnected_install_flow": [["폐쇄망", "disconnected"], ["순서", "절차"], ["미러", "미러링", "oc-mirror", "mirror registry"]],
    "disconnected_update_flow": [["폐쇄망", "disconnected"], ["업데이트", "update"], ["미러", "미러링", "oc-mirror", "OSUS"]],
    "must_gather_usage": [["must-gather"], ["수집", "진단", "지원"]],
    "node_notready": [["NotReady", "노드"], ["확인", "점검"], ["원인", "조치"]],
    "operator_degraded": [["operator", "Operator"], ["degraded", "저하"], ["확인", "점검"]],
    "etcd_backup": [["etcd"], ["백업", "backup"]],
    "etcd_recovery": [["etcd"], ["복구", "restore", "recovery"]],
}


@dataclass
class GoldenCase:
    id: str
    group: str
    scope_policy: str
    question_ko: str
    intent_category: str
    expected_source_scope: str
    expected_answer_shape: str


def parse_scope_paths(raw_scope: str) -> list[str]:
    if raw_scope.startswith("NONE"):
        return []
    _, _, remainder = raw_scope.partition(":")
    if not remainder:
        return []
    paths = []
    for item in remainder.split(";"):
        path = item.strip()
        if not path:
            continue
        paths.append(path)
    return paths


def derive_source_dirs(paths: list[str]) -> list[str]:
    dirs: list[str] = []
    for path in paths:
        top_level = path.split("/", 1)[0].strip()
        if top_level and top_level not in dirs:
            dirs.append(top_level)
    return dirs


def extract_domain_terms(question: str) -> list[str]:
    found: list[str] = []
    lowered = question.lower()
    for keyword in DOMAIN_KEYWORDS:
        if keyword.lower() in lowered and keyword not in found:
            found.append(keyword)
    return found


def extract_korean_terms(question: str) -> list[str]:
    normalized = re.sub(r"[^0-9A-Za-z가-힣\\-\\. ]+", " ", question)
    tokens = [token.strip() for token in normalized.split() if token.strip()]
    selected: list[str] = []
    for token in tokens:
        for suffix in TRAILING_PARTICLES:
            if token.endswith(suffix) and len(token) > len(suffix) + 1:
                token = token[: -len(suffix)]
                break
        if token in STOPWORDS:
            continue
        if len(token) <= 1:
            continue
        if re.fullmatch(r"[0-9.]+", token):
            continue
        if token not in selected:
            selected.append(token)
    return selected


def shape_keyword_groups(expected_answer_shape: str) -> list[list[str]]:
    groups: list[list[str]] = []
    for key, keywords in SHAPE_RULES.items():
        if key in expected_answer_shape:
            groups.append(keywords)
    return groups


def refusal_keywords(question: str) -> list[str]:
    base = ["범위", "공식 OCP", "지원하지", "추정하지", "별도 문서", "별도 제품"]
    for product, aliases in OUT_OF_SCOPE_PRODUCTS.items():
        if any(alias.lower() in question.lower() for alias in aliases):
            return base + aliases
    return base


def forbidden_keywords(scope_policy: str) -> list[str]:
    if scope_policy == "out_of_scope":
        return []
    return ["ROSA", "OSD", "OCM", "MicroShift", "Lightspeed", "HyperShift"]


def build_keyword_groups(case: GoldenCase) -> list[list[str]]:
    groups: list[list[str]] = []
    groups.extend(GROUP_REQUIRED_KEYWORD_GROUPS.get(case.group, []))
    groups.extend(INTENT_REQUIRED_KEYWORD_GROUPS.get(case.intent_category, []))
    for term in extract_domain_terms(case.question_ko)[:3]:
        groups.append([term])
    korean_terms = extract_korean_terms(case.question_ko)
    for term in korean_terms[:3]:
        groups.append([term])
    groups.extend(shape_keyword_groups(case.expected_answer_shape))

    deduped: list[list[str]] = []
    seen: set[tuple[str, ...]] = set()
    for group in groups:
        normalized = tuple(dict.fromkeys(group))
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(list(normalized))
    return deduped


def build_case_record(case: GoldenCase, expected_paths: list[str]) -> dict[str, object]:
    in_scope = case.scope_policy == "in_scope"
    return {
        "id": case.id,
        "scenario_id": case.id.lower(),
        "turn_index": 1,
        "turn_type": "standalone",
        "group": case.group,
        "question_ko": case.question_ko,
        "expected_source_dirs": derive_source_dirs(expected_paths),
        "expected_document_paths": expected_paths,
        "expected_category": GROUP_CATEGORY_MAP.get(case.group, "other"),
        "expected_version_behavior": "stable",
        "expected_query_class": case.intent_category,
        "expected_memory_behavior": "standalone",
        "citation_required": in_scope,
        "click_through_required": in_scope,
        "context_harness_required": False,
        "must_include_terms": extract_domain_terms(case.question_ko)[:3] + extract_korean_terms(case.question_ko)[:3],
        "must_not_include_terms": forbidden_keywords(case.scope_policy),
        "notes": case.expected_answer_shape,
    }


def build_rubric_record(case: GoldenCase, expected_paths: list[str]) -> dict[str, object]:
    in_scope = case.scope_policy == "in_scope"
    expected_source_dirs = derive_source_dirs(expected_paths)
    return {
        "id": case.id,
        "group": case.group,
        "scope_policy": case.scope_policy,
        "intent_category": case.intent_category,
        "question_ko": case.question_ko,
        "expected_document_paths": expected_paths,
        "expected_source_dirs": expected_source_dirs,
        "expected_answer_shape": case.expected_answer_shape,
        "required_keyword_groups": build_keyword_groups(case) if in_scope else [],
        "required_source_scope_terms": expected_source_dirs,
        "forbidden_keywords": forbidden_keywords(case.scope_policy),
        "refusal_required": not in_scope,
        "refusal_any_keywords": refusal_keywords(case.question_ko) if not in_scope else [],
        "min_citation_count": 1 if in_scope else 0,
        "max_citation_count": 3 if in_scope else 0,
    }


def load_cases() -> list[GoldenCase]:
    rows: list[GoldenCase] = []
    with GOLDEN_SET_CSV.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(
                GoldenCase(
                    id=row["id"].strip(),
                    group=row["group"].strip(),
                    scope_policy=row["scope_policy"].strip(),
                    question_ko=row["question_ko"].strip(),
                    intent_category=row["intent_category"].strip(),
                    expected_source_scope=row["expected_source_scope"].strip(),
                    expected_answer_shape=row["expected_answer_shape"].strip(),
                )
            )
    return rows


def main() -> None:
    cases = load_cases()
    benchmark_lines: list[str] = []
    rubric_records: list[dict[str, object]] = []

    for case in cases:
        expected_paths = parse_scope_paths(case.expected_source_scope)
        benchmark_lines.append(json.dumps(build_case_record(case, expected_paths), ensure_ascii=False))
        rubric_records.append(build_rubric_record(case, expected_paths))

    CASES_OUT.parent.mkdir(parents=True, exist_ok=True)
    CASES_OUT.write_text("\n".join(benchmark_lines) + "\n", encoding="utf-8")
    RUBRIC_OUT.write_text(json.dumps(rubric_records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"case_count": len(cases), "cases_out": str(CASES_OUT), "rubric_out": str(RUBRIC_OUT)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
