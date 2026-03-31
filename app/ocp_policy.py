from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml


VERSION_PATTERN = re.compile(r"(?<!\d)(4\.\d{1,2}|4\.x)(?!\d)", re.IGNORECASE)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "")).strip().lower()


def _normalize_path(value: str) -> str:
    return value.replace("\\", "/").strip().lower()


@dataclass(frozen=True)
class QuerySignals:
    question_ko: str
    mode: str
    normalized_question: str
    preferred_categories: tuple[str, ...]
    preferred_source_dirs: tuple[str, ...]
    path_terms: tuple[str, ...]
    matched_rules: tuple[str, ...]
    version_hint: str
    follow_up_detected: bool
    risk_notice_required: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "question_ko": self.question_ko,
            "mode": self.mode,
            "preferred_categories": list(self.preferred_categories),
            "preferred_source_dirs": list(self.preferred_source_dirs),
            "path_terms": list(self.path_terms),
            "matched_rules": list(self.matched_rules),
            "version_hint": self.version_hint,
            "follow_up_detected": self.follow_up_detected,
            "risk_notice_required": self.risk_notice_required,
        }


class OcpPolicyEngine:
    def __init__(self, policy_data: dict[str, Any]) -> None:
        self.policy = policy_data
        self.answering = policy_data.get("answering", {})
        self.modes = policy_data.get("modes", {})
        self.retrieval = policy_data.get("retrieval", {})
        self.memory = policy_data.get("memory", {})

    @classmethod
    def from_path(cls, path: Path | None = None) -> "OcpPolicyEngine":
        config_path = path or (_repo_root() / "configs" / "rag-policy.yaml")
        payload = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        return cls(payload)

    def analyze_query(
        self,
        question_ko: str,
        *,
        mode: str = "operations",
        memory_state: dict[str, Any] | None = None,
    ) -> QuerySignals:
        memory_state = memory_state or {}
        normalized_question = _normalize_text(question_ko)
        preferred_categories: list[str] = []
        preferred_source_dirs: list[str] = []
        path_terms: list[str] = []
        matched_rules: list[str] = []
        version_hint = self._extract_version(question_ko) or str(memory_state.get("active_version", "")).strip()

        for rule_name, rule in (self.retrieval.get("query_signal_rules", {}) or {}).items():
            terms = [_normalize_text(term) for term in rule.get("any_terms", [])]
            if not terms:
                continue
            if any(term and term in normalized_question for term in terms):
                matched_rules.append(rule_name)
                self._extend_unique(preferred_categories, rule.get("preferred_categories", []))
                self._extend_unique(preferred_source_dirs, rule.get("preferred_source_dirs", []))
                self._extend_unique(path_terms, rule.get("path_terms", []))

        follow_up_detected = self._is_follow_up(question_ko, memory_state)
        if follow_up_detected:
            self._extend_unique(preferred_source_dirs, memory_state.get("active_source_dirs", []))
            self._extend_unique(preferred_categories, memory_state.get("active_categories", []))
            active_doc_path = str(memory_state.get("active_document_path", "")).strip()
            if active_doc_path:
                path_terms.extend([segment for segment in _normalize_path(active_doc_path).split("/") if segment])

        risk_categories = set(self.modes.get(mode, {}).get("require_risk_notice_for", []))
        risk_notice_required = any(category in risk_categories for category in preferred_categories)

        return QuerySignals(
            question_ko=question_ko,
            mode=mode,
            normalized_question=normalized_question,
            preferred_categories=tuple(preferred_categories),
            preferred_source_dirs=tuple(preferred_source_dirs),
            path_terms=tuple(path_terms),
            matched_rules=tuple(matched_rules),
            version_hint=version_hint,
            follow_up_detected=follow_up_detected,
            risk_notice_required=risk_notice_required,
        )

    def rerank_candidates(
        self,
        question_ko: str,
        candidates: list[dict[str, Any]],
        *,
        mode: str = "operations",
        memory_state: dict[str, Any] | None = None,
        signals: QuerySignals | None = None,
    ) -> tuple[list[dict[str, Any]], QuerySignals]:
        signals = signals or self.analyze_query(question_ko, mode=mode, memory_state=memory_state)
        ranked_candidates: list[dict[str, Any]] = []

        for candidate in candidates:
            prepared_candidate = dict(candidate)
            prepared_candidate["effective_category"] = self.effective_category(prepared_candidate)
            score, breakdown = self._score_candidate(prepared_candidate, signals, memory_state or {})
            prepared_candidate["policy_score"] = round(score, 4)
            prepared_candidate["policy_breakdown"] = breakdown
            ranked_candidates.append(prepared_candidate)

        ranked_candidates.sort(
            key=lambda item: (
                -float(item.get("policy_score", 0.0)),
                int(item.get("rank", 999999)),
                _normalize_path(str(item.get("document_path", ""))),
            )
        )

        for index, candidate in enumerate(ranked_candidates, start=1):
            candidate["rank"] = index

        return ranked_candidates, signals

    def augment_follow_up_candidates(
        self,
        question_ko: str,
        candidates: list[dict[str, Any]],
        *,
        manifest_index: dict[str, dict[str, Any]],
        mode: str = "operations",
        memory_state: dict[str, Any] | None = None,
        signals: QuerySignals | None = None,
    ) -> tuple[list[dict[str, Any]], QuerySignals]:
        memory_state = memory_state or {}
        signals = signals or self.analyze_query(question_ko, mode=mode, memory_state=memory_state)
        augmented = [dict(candidate) for candidate in candidates]
        augmented = self._augment_manifest_hint_candidates(
            augmented,
            manifest_index=manifest_index,
            signals=signals,
            memory_state=memory_state,
        )

        if not signals.follow_up_detected:
            return augmented, signals

        active_document_path = _normalize_path(str(memory_state.get("active_document_path", "")))
        if not active_document_path:
            return augmented, signals

        if any(_normalize_path(str(item.get("document_path", ""))) == active_document_path for item in augmented):
            return augmented, signals

        manifest_doc = manifest_index.get(active_document_path)
        if not manifest_doc:
            return augmented, signals

        if not self._should_rescue_active_document(manifest_doc, active_document_path, signals):
            return augmented, signals

        sections = manifest_doc.get("sections", []) or []
        section_title = sections[0].get("section_title", "") if sections else ""
        rescue_score = self._memory_anchor_score(augmented)
        augmented.append(
            {
                "rank": len(augmented) + 1,
                "source_dir": manifest_doc.get("top_level_dir", ""),
                "document_path": active_document_path,
                "viewer_url": manifest_doc.get("viewer_url", ""),
                "score": rescue_score,
                "section_title": section_title,
                "title": manifest_doc.get("title", ""),
                "product": manifest_doc.get("product", ""),
                "version": manifest_doc.get("version", ""),
                "category": manifest_doc.get("category", ""),
                "trust_level": manifest_doc.get("trust_level", ""),
                "top_level_dir": manifest_doc.get("top_level_dir", ""),
                "retrieval_origin": "memory_anchor",
            }
        )
        return augmented, signals

    def _augment_manifest_hint_candidates(
        self,
        candidates: list[dict[str, Any]],
        *,
        manifest_index: dict[str, dict[str, Any]],
        signals: QuerySignals,
        memory_state: dict[str, Any],
    ) -> list[dict[str, Any]]:
        if not manifest_index:
            return candidates

        preferred_source_dirs = {str(item).strip().lower() for item in signals.preferred_source_dirs if item}
        preferred_categories = {str(item).strip().lower() for item in signals.preferred_categories if item}
        normalized_path_terms = [_normalize_text(term) for term in signals.path_terms if _normalize_text(term)]
        if not (preferred_source_dirs or preferred_categories or normalized_path_terms):
            return candidates

        scan_limit = max(int(self.retrieval.get("manifest_hint_scan_limit", 5)), 1)
        top_candidates = candidates[:scan_limit]
        top_source_dirs = {
            str(candidate.get("source_dir") or candidate.get("top_level_dir", "")).strip().lower()
            for candidate in top_candidates
            if candidate.get("source_dir") or candidate.get("top_level_dir")
        }
        top_categories = {
            self.effective_category(candidate).strip().lower()
            for candidate in top_candidates
            if self.effective_category(candidate)
        }
        top_path_hits = max(
            (self._count_candidate_path_term_hits(candidate, normalized_path_terms) for candidate in top_candidates),
            default=0,
        )

        rescue_needed = False
        if preferred_source_dirs and not (top_source_dirs & preferred_source_dirs):
            rescue_needed = True
        elif preferred_categories and not (top_categories & preferred_categories):
            rescue_needed = True
        elif normalized_path_terms and top_path_hits == 0:
            rescue_needed = True

        if not rescue_needed:
            return candidates

        existing_paths = {_normalize_path(str(candidate.get("document_path", ""))) for candidate in candidates}
        base_score = self._manifest_hint_base_score(candidates)
        hint_limit = max(int(self.retrieval.get("manifest_hint_limit", 2)), 1)
        hint_candidates: list[dict[str, Any]] = []

        for document_path, manifest_doc in manifest_index.items():
            normalized_document_path = _normalize_path(document_path)
            if normalized_document_path in existing_paths:
                continue

            score, breakdown = self._manifest_hint_score(
                manifest_doc,
                preferred_source_dirs=preferred_source_dirs,
                preferred_categories=preferred_categories,
                normalized_path_terms=normalized_path_terms,
                memory_state=memory_state,
                base_score=base_score,
            )
            if score <= 0.0:
                continue

            hint_candidates.append(
                {
                    "rank": len(candidates) + len(hint_candidates) + 1,
                    "source_dir": manifest_doc.get("top_level_dir", ""),
                    "document_path": normalized_document_path,
                    "viewer_url": manifest_doc.get("viewer_url", ""),
                    "score": score,
                    "section_title": self._select_manifest_section_title(manifest_doc, normalized_path_terms),
                    "title": manifest_doc.get("title", ""),
                    "product": manifest_doc.get("product", ""),
                    "version": manifest_doc.get("version", ""),
                    "category": manifest_doc.get("category", ""),
                    "trust_level": manifest_doc.get("trust_level", ""),
                    "top_level_dir": manifest_doc.get("top_level_dir", ""),
                    "retrieval_origin": "policy_manifest_hint",
                    "policy_hint_breakdown": breakdown,
                }
            )

        hint_candidates.sort(
            key=lambda item: (
                -float(item.get("score", 0.0)),
                _normalize_path(str(item.get("document_path", ""))),
            )
        )
        return candidates + hint_candidates[:hint_limit]

    def build_answer_contract(
        self,
        question_ko: str,
        ranked_candidates: list[dict[str, Any]],
        *,
        mode: str = "operations",
        grounded: bool | None = None,
        memory_state: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        signals = self.analyze_query(question_ko, mode=mode, memory_state=memory_state)
        top_candidates = ranked_candidates[: self.answering.get("citation_style", {}).get("max_sources", 3)]
        explicit_grounded = grounded if grounded is not None else bool(top_candidates)
        technical_term_rule = "원문 기술 용어와 명령어는 번역하지 않습니다." if self.answering.get("preserve_technical_terms") else ""
        mode_config = self.modes.get(mode, {})

        instructions = [
            f"답변 언어는 {self.answering.get('default_language', 'ko')}입니다.",
            f"응답 톤은 {mode_config.get('tone', 'concise')}입니다.",
            self.answering.get("operations_conservative_notice", "").strip(),
            technical_term_rule,
        ]

        if self.answering.get("require_citations"):
            instructions.append("모든 핵심 주장 뒤에 출처를 붙입니다.")

        if signals.risk_notice_required:
            instructions.append("업데이트/보안/트러블슈팅 성격의 질문이므로 위험하거나 파괴적인 작업 전 주의 문구를 포함합니다.")

        if signals.version_hint:
            instructions.append(f"버전 문맥은 {signals.version_hint} 기준으로 유지합니다.")
        elif self.answering.get("disclose_version_uncertainty"):
            instructions.append("버전이 명시되지 않으면 4.x 기준 일반 가이드를 따르되, 버전 차이가 있을 수 있음을 짧게 알립니다.")

        if not explicit_grounded and self.answering.get("refuse_if_ungrounded"):
            instructions.append(self.answering.get("ungrounded_response_ko", "").strip())

        return {
            "mode": mode,
            "grounded": explicit_grounded,
            "signals": signals.to_dict(),
            "top_document_paths": [candidate.get("document_path", "") for candidate in top_candidates],
            "instructions": [item for item in instructions if item],
        }

    def _score_candidate(
        self,
        candidate: dict[str, Any],
        signals: QuerySignals,
        memory_state: dict[str, Any],
    ) -> tuple[float, dict[str, float]]:
        scoring = self.retrieval.get("scoring", {})
        source_priority = self.retrieval.get("source_priority", {})
        source_dir_priority = self.retrieval.get("source_dir_priority", {})
        category_priority = self.retrieval.get("category_priority", {})
        product_policy = self.retrieval.get("product_policy", {})
        version_policy = self.retrieval.get("version_policy", {})

        breakdown: dict[str, float] = {}
        total = 0.0

        base_score = float(candidate.get("score", 0.0)) * float(self.retrieval.get("base_similarity_multiplier", 100.0))
        breakdown["base_similarity"] = round(base_score, 4)
        total += base_score

        trust_level = str(candidate.get("trust_level", "reference")).strip()
        trust_boost = float(source_priority.get(trust_level, 0)) / 10.0
        breakdown["trust_level"] = round(trust_boost, 4)
        total += trust_boost

        product = str(candidate.get("product", "")).strip().lower()
        allowed_products = {str(item).lower() for item in product_policy.get("allowed_products", [])}
        blocked_products = {str(item).lower() for item in product_policy.get("blocked_products", [])}
        if product and product in blocked_products:
            blocked_penalty = -float(scoring.get("blocked_product_penalty", 200))
            breakdown["blocked_product_penalty"] = round(blocked_penalty, 4)
            total += blocked_penalty
        elif product and allowed_products and product not in allowed_products:
            penalty = -float(scoring.get("nonpreferred_product_penalty", 25))
            breakdown["nonpreferred_product_penalty"] = round(penalty, 4)
            total += penalty

        source_dir = str(candidate.get("source_dir") or candidate.get("top_level_dir", "")).strip()
        if source_dir:
            source_dir_weight = float(source_dir_priority.get(source_dir, 0)) / 12.0
            breakdown["source_dir_priority"] = round(source_dir_weight, 4)
            total += source_dir_weight

            if signals.preferred_source_dirs:
                if source_dir in signals.preferred_source_dirs:
                    boost = float(scoring.get("source_dir_match_boost", 9))
                    breakdown["source_dir_match"] = round(boost, 4)
                    total += boost
                else:
                    penalty = -float(scoring.get("source_dir_mismatch_penalty", 3))
                    breakdown["source_dir_mismatch"] = round(penalty, 4)
                    total += penalty

        category = self.effective_category(candidate)
        category_weight = float(category_priority.get(category, category_priority.get("other", 0))) / 14.0
        breakdown["category_priority"] = round(category_weight, 4)
        total += category_weight

        if signals.preferred_categories:
            if category in signals.preferred_categories:
                boost = float(scoring.get("category_match_boost", 7))
                breakdown["category_match"] = round(boost, 4)
                total += boost
            else:
                penalty = -float(scoring.get("category_mismatch_penalty", 2))
                breakdown["category_mismatch"] = round(penalty, 4)
                total += penalty

        memory_source_dirs = [str(item) for item in memory_state.get("active_source_dirs", []) if item]
        if source_dir and source_dir in memory_source_dirs:
            boost = float(scoring.get("memory_source_dir_boost", 8))
            breakdown["memory_source_dir"] = round(boost, 4)
            total += boost

        memory_categories = [str(item) for item in memory_state.get("active_categories", []) if item]
        if category and category in memory_categories:
            boost = float(scoring.get("memory_category_boost", 4))
            breakdown["memory_category"] = round(boost, 4)
            total += boost

        memory_document_path = _normalize_path(str(memory_state.get("active_document_path", "")))
        candidate_document_path = _normalize_path(str(candidate.get("document_path", "")))
        if memory_document_path and candidate_document_path == memory_document_path:
            boost = float(scoring.get("memory_document_boost", 6))
            breakdown["memory_document"] = round(boost, 4)
            total += boost

        searchable_text = " ".join(
            [
                _normalize_text(str(candidate.get("title", ""))),
                _normalize_text(str(candidate.get("document_path", ""))),
                _normalize_text(str(candidate.get("section_title", ""))),
            ]
        )
        matched_path_terms = 0
        for term in signals.path_terms:
            normalized_term = _normalize_text(term)
            if normalized_term and normalized_term in searchable_text:
                matched_path_terms += 1
        path_term_boost = matched_path_terms * float(scoring.get("path_term_boost", 1.5))
        breakdown["path_term_match"] = round(path_term_boost, 4)
        total += path_term_boost

        candidate_version = str(candidate.get("version", "")).strip()
        if signals.version_hint and candidate_version:
            if candidate_version == signals.version_hint:
                boost = float(version_policy.get("continuity_boost", 8))
                breakdown["version_match"] = round(boost, 4)
                total += boost
            elif version_policy.get("reject_unknown_version_mix"):
                penalty = -float(version_policy.get("mismatch_penalty", 20))
                breakdown["version_mismatch"] = round(penalty, 4)
                total += penalty
        elif not candidate_version and version_policy.get("reject_unknown_version_mix"):
            penalty = -float(version_policy.get("unknown_penalty", 4))
            breakdown["version_unknown"] = round(penalty, 4)
            total += penalty

        return total, breakdown

    def effective_category(self, candidate: dict[str, Any]) -> str:
        raw_category = str(candidate.get("category", "")).strip()
        document_path = _normalize_path(str(candidate.get("document_path", "")))
        source_dir = str(candidate.get("source_dir") or candidate.get("top_level_dir", "")).strip().lower()

        if "/troubleshooting/" in document_path or source_dir == "support":
            return "troubleshooting"
        if "/updating/" in document_path or source_dir == "updating":
            return "upgrade"
        if "security" in document_path:
            return "security"
        if "network" in document_path:
            return "networking"
        if "storage" in document_path:
            return "storage"
        if raw_category:
            return raw_category
        return "other"

    def _should_rescue_active_document(
        self,
        manifest_doc: dict[str, Any],
        active_document_path: str,
        signals: QuerySignals,
    ) -> bool:
        source_dir = str(manifest_doc.get("top_level_dir", "")).strip().lower()
        effective_category = self.effective_category(
            {
                "category": manifest_doc.get("category", ""),
                "document_path": active_document_path,
                "source_dir": source_dir,
                "top_level_dir": source_dir,
            }
        )

        if signals.preferred_source_dirs and source_dir in {
            item.strip().lower() for item in signals.preferred_source_dirs if item
        }:
            return True
        if signals.preferred_categories and effective_category in {
            item.strip().lower() for item in signals.preferred_categories if item
        }:
            return True
        return not signals.preferred_source_dirs and not signals.preferred_categories

    def _manifest_hint_score(
        self,
        manifest_doc: dict[str, Any],
        *,
        preferred_source_dirs: set[str],
        preferred_categories: set[str],
        normalized_path_terms: list[str],
        memory_state: dict[str, Any],
        base_score: float,
    ) -> tuple[float, dict[str, float]]:
        top_level_dir = str(manifest_doc.get("top_level_dir", "")).strip().lower()
        effective_category = self.effective_category(
            {
                "category": manifest_doc.get("category", ""),
                "document_path": manifest_doc.get("source_url", ""),
                "source_dir": top_level_dir,
                "top_level_dir": top_level_dir,
            }
        ).strip().lower()
        path_term_hits = self._count_manifest_path_term_hits(manifest_doc, normalized_path_terms)
        source_dir_match = bool(top_level_dir and top_level_dir in preferred_source_dirs)
        category_match = bool(effective_category and effective_category in preferred_categories)

        if path_term_hits == 0 and not source_dir_match and not category_match:
            return 0.0, {}

        breakdown: dict[str, float] = {"base_score": round(base_score, 6)}
        score = base_score

        if source_dir_match:
            score += 0.006
            breakdown["source_dir_match"] = 0.006
        if category_match:
            score += 0.003
            breakdown["category_match"] = 0.003
        if path_term_hits:
            path_boost = min(path_term_hits, 4) * 0.004
            score += path_boost
            breakdown["path_term_hits"] = round(path_boost, 6)

        active_source_dirs = {str(item).strip().lower() for item in memory_state.get("active_source_dirs", []) if item}
        if top_level_dir and top_level_dir in active_source_dirs:
            score += 0.002
            breakdown["memory_source_dir"] = 0.002

        return round(min(score, 0.999999), 6), breakdown

    def _count_manifest_path_term_hits(self, manifest_doc: dict[str, Any], normalized_path_terms: list[str]) -> int:
        searchable_parts = [
            str(manifest_doc.get("title", "")),
            str(manifest_doc.get("source_url", "")),
            str(manifest_doc.get("local_path", "")),
            str(manifest_doc.get("viewer_url", "")),
        ]
        searchable_parts.extend(str(section.get("section_title", "")) for section in (manifest_doc.get("sections", []) or []))
        searchable_text = _normalize_text(" ".join(searchable_parts))
        return sum(1 for term in normalized_path_terms if term and term in searchable_text)

    def _count_candidate_path_term_hits(self, candidate: dict[str, Any], normalized_path_terms: list[str]) -> int:
        searchable_text = _normalize_text(
            " ".join(
                [
                    str(candidate.get("title", "")),
                    str(candidate.get("document_path", "")),
                    str(candidate.get("section_title", "")),
                ]
            )
        )
        return sum(1 for term in normalized_path_terms if term and term in searchable_text)

    def _select_manifest_section_title(self, manifest_doc: dict[str, Any], normalized_path_terms: list[str]) -> str:
        sections = manifest_doc.get("sections", []) or []
        if not sections:
            return ""
        if not normalized_path_terms:
            return str(sections[0].get("section_title", ""))

        best_title = str(sections[0].get("section_title", ""))
        best_hits = -1
        for section in sections:
            title = str(section.get("section_title", ""))
            searchable_text = _normalize_text(
                " ".join(
                    [
                        title,
                        str(section.get("section_anchor", "")),
                        " ".join(section.get("heading_hierarchy", []) or []),
                    ]
                )
            )
            hits = sum(1 for term in normalized_path_terms if term and term in searchable_text)
            if hits > best_hits:
                best_hits = hits
                best_title = title
        return best_title

    def _extract_version(self, question_ko: str) -> str:
        match = VERSION_PATTERN.search(question_ko)
        return match.group(1) if match else ""

    def _is_follow_up(self, question_ko: str, memory_state: dict[str, Any]) -> bool:
        normalized_question = _normalize_text(question_ko)
        if not memory_state:
            return False
        cues = [_normalize_text(cue) for cue in self.memory.get("follow_up_cues", [])]
        if any(cue and cue in normalized_question for cue in cues):
            return True
        return bool(memory_state.get("active_document_path")) and len(question_ko.strip()) <= 48

    @staticmethod
    def _extend_unique(target: list[str], values: list[Any]) -> None:
        for value in values:
            item = str(value).strip()
            if item and item not in target:
                target.append(item)

    @staticmethod
    def _memory_anchor_score(candidates: list[dict[str, Any]]) -> float:
        if not candidates:
            return 0.05
        numeric_scores = [float(candidate.get("score", 0.0)) for candidate in candidates if candidate.get("score") is not None]
        if not numeric_scores:
            return 0.05
        ceiling = max(numeric_scores)
        floor = min(numeric_scores)
        return round(max(ceiling * 0.97, floor * 1.05, 0.05), 6)

    @staticmethod
    def _manifest_hint_base_score(candidates: list[dict[str, Any]]) -> float:
        if not candidates:
            return 0.35
        numeric_scores = [float(candidate.get("score", 0.0)) for candidate in candidates if candidate.get("score") is not None]
        if not numeric_scores:
            return 0.35
        ceiling = max(numeric_scores)
        floor = min(numeric_scores)
        return round(max(ceiling * 0.94, floor * 1.02, 0.35), 6)


@lru_cache(maxsize=1)
def load_policy_engine() -> OcpPolicyEngine:
    return OcpPolicyEngine.from_path()
