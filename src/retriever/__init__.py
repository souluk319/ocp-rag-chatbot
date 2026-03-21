"""
검색 + 리랭킹. IVF에서 후보를 넉넉히 뽑고(top_k*3),
semantic score와 BM25 keyword score를 섞어서 최종 순위 결정.
"""
import re
import math
import numpy as np
from collections import Counter
from dataclasses import dataclass

from src.vectorstore import IVFIndex, SearchResult
from src.embedding import EmbeddingEngine
from src.config import TOP_K


@dataclass
class RankedResult:
    """리랭킹 후 최종 결과"""
    chunk_id: str
    text: str
    score: float
    semantic_score: float
    keyword_score: float
    metadata: dict


class BM25Scorer:
    """BM25 키워드 매칭 스코어러

    두 가지 모드:
    1. score(): 후보군 내 reranking (기존)
    2. search_corpus(): 전체 코퍼스에서 독립 검색 (신규)
       - 임베딩 모델이 못 잡는 키워드 매칭 문서를 보완
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        # 전체 코퍼스 인덱스 (서버 시작 시 구축)
        self._corpus_tokens: list[list[str]] = []
        self._corpus_doc_lengths: list[int] = []
        self._corpus_avg_dl: float = 0
        self._corpus_doc_freq: Counter = Counter()
        self._corpus_size: int = 0
        self._indexed = False

    def index_corpus(self, documents: list[dict]):
        """전체 코퍼스 인덱싱 (서버 시작 시 1회 호출)

        Args:
            documents: IVFIndex.documents [{chunk_id, text, metadata}, ...]
        """
        self._corpus_tokens = [self._tokenize(doc["text"]) for doc in documents]
        self._corpus_doc_lengths = [len(t) for t in self._corpus_tokens]
        self._corpus_avg_dl = (
            sum(self._corpus_doc_lengths) / len(self._corpus_doc_lengths)
            if self._corpus_doc_lengths else 1
        )
        self._corpus_doc_freq = Counter()
        for tokens in self._corpus_tokens:
            for token in set(tokens):
                self._corpus_doc_freq[token] += 1
        self._corpus_size = len(documents)
        self._indexed = True

    def search_corpus(self, query: str, top_k: int = 10) -> list[tuple[int, float]]:
        """전체 코퍼스에서 BM25 상위 top_k 검색

        Returns:
            [(doc_index, raw_bm25_score), ...] 내림차순
        """
        if not self._indexed:
            return []

        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        scores = []
        for i, tokens in enumerate(self._corpus_tokens):
            tf_counts = Counter(tokens)
            dl = self._corpus_doc_lengths[i]
            score = 0.0
            for qt in query_tokens:
                tf = tf_counts.get(qt, 0)
                df = self._corpus_doc_freq.get(qt, 0)
                if tf == 0 or df == 0:
                    continue
                idf = math.log(
                    (self._corpus_size - df + 0.5) / (df + 0.5) + 1
                )
                tf_norm = (tf * (self.k1 + 1)) / (
                    tf + self.k1 * (1 - self.b + self.b * dl / self._corpus_avg_dl)
                )
                score += idf * tf_norm
            scores.append(score)

        # 상위 top_k 인덱스 (score > 0인 것만)
        indexed_scores = [(i, s) for i, s in enumerate(scores) if s > 0]
        indexed_scores.sort(key=lambda x: x[1], reverse=True)
        return indexed_scores[:top_k]

    # OCP/K8s 한영 동의어 매핑 — BM25가 "파드"로 검색해도 "Pod" 문서를 찾도록
    _SYNONYMS: dict[str, list[str]] = {
        "pod": ["파드"],
        "파드": ["pod"],
        "node": ["노드"],
        "노드": ["node"],
        "openshift": ["오픈시프트", "ocp"],
        "오픈시프트": ["openshift", "ocp"],
        "ocp": ["openshift", "오픈시프트"],
        "login": ["로그인"],
        "로그인": ["login"],
        "deploy": ["배포", "디플로이"],
        "배포": ["deploy"],
        "container": ["컨테이너"],
        "컨테이너": ["container"],
        "cluster": ["클러스터"],
        "클러스터": ["cluster"],
        "namespace": ["네임스페이스", "프로젝트"],
        "네임스페이스": ["namespace"],
        "service": ["서비스"],
        "서비스": ["service"],
        "route": ["라우트"],
        "라우트": ["route"],
        "image": ["이미지"],
        "이미지": ["image"],
        "registry": ["레지스트리"],
        "레지스트리": ["registry"],
        "secret": ["시크릿"],
        "시크릿": ["secret"],
        "volume": ["볼륨"],
        "볼륨": ["volume"],
        "storage": ["스토리지"],
        "스토리지": ["storage"],
        "pending": ["펜딩", "대기"],
        "troubleshooting": ["트러블슈팅", "문제해결"],
        "트러블슈팅": ["troubleshooting"],
        "error": ["에러", "오류"],
        "에러": ["error"],
        "cli": ["명령줄"],
    }

    def _tokenize(self, text: str) -> list[str]:
        """공백 기반 단어 단위 토크나이저 + 동의어 확장.

        이전 버전은 한글을 글자 단위로 쪼개서("상태" → "상","태") BM25가 무력화됨.
        개선: 공백 기준으로 분리 후 한글 연속 문자열을 단어로 유지.
        추가: 동의어 매핑으로 한영 교차 검색 지원 ("파드" 검색 → "pod" 문서 매칭).
        """
        text = text.lower()
        words = text.split()
        tokens = []
        for word in words:
            # 영문+숫자 토큰 (하이픈 포함 기술용어 대응: crash-loop 등)
            en_tokens = re.findall(r"[a-z][a-z0-9\-]*[a-z0-9]|[a-z0-9]+", word)
            # 한국어 연속 문자열 = 단어 단위 유지 (2글자 이상)
            ko_tokens = re.findall(r"[가-힣]{2,}", word)
            tokens.extend(en_tokens)
            tokens.extend(ko_tokens)
        # 한국어 조사 제거 — "클러스터에" → "클러스터", "로그인하는" → "로그인"
        stripped = []
        for token in tokens:
            s = self._strip_josa(token)
            stripped.append(s)
        # 동의어 확장
        expanded = list(stripped)
        for token in stripped:
            synonyms = self._SYNONYMS.get(token, [])
            for syn in synonyms:
                if syn not in expanded:
                    expanded.append(syn)
        return expanded

    @staticmethod
    def _strip_josa(token: str) -> str:
        """한국어 토큰에서 흔한 조사/어미를 제거.

        형태소 분석기 없이 접미사 패턴 매칭으로 처리.
        완벽하지 않지만 BM25 매칭률을 크게 개선.
        """
        if not token or not ('가' <= token[-1] <= '힣'):
            return token
        # 긴 접미사부터 매칭 (greedy)
        suffixes = [
            "에서는", "으로는", "에서의", "으로의",
            "하는", "에서", "으로", "이란", "란",
            "에는", "과는", "와는", "처럼",
            "에게", "한테", "보다", "까지", "부터", "마다",
            "이나", "거나", "든지",
            "의", "에", "를", "을", "은", "는", "이", "가",
            "와", "과", "로", "도", "만",
        ]
        for suffix in suffixes:
            if len(token) > len(suffix) and token.endswith(suffix):
                return token[:-len(suffix)]
        return token

    def score(self, query: str, documents: list[str]) -> list[float]:
        """BM25 스코어 계산"""
        if not documents:
            return []

        query_tokens = self._tokenize(query)
        if not query_tokens:
            return [0.0] * len(documents)

        # 문서별 토큰화
        doc_tokens = [self._tokenize(doc) for doc in documents]
        doc_lengths = [len(tokens) for tokens in doc_tokens]
        avg_dl = sum(doc_lengths) / len(doc_lengths) if doc_lengths else 1

        # IDF 계산 (후보군 기준)
        n_docs = len(documents)
        doc_freq = Counter()
        for tokens in doc_tokens:
            unique_tokens = set(tokens)
            for token in unique_tokens:
                doc_freq[token] += 1

        scores = []
        for i, tokens in enumerate(doc_tokens):
            tf_counts = Counter(tokens)
            dl = doc_lengths[i]
            score = 0.0
            for qt in query_tokens:
                tf = tf_counts.get(qt, 0)
                df = doc_freq.get(qt, 0)
                if tf == 0 or df == 0:
                    continue
                idf = math.log((n_docs - df + 0.5) / (df + 0.5) + 1)
                tf_norm = (tf * (self.k1 + 1)) / (tf + self.k1 * (1 - self.b + self.b * dl / avg_dl))
                score += idf * tf_norm
            scores.append(score)

        # 정규화 (0~1 범위)
        max_score = max(scores) if scores else 1
        if max_score > 0:
            scores = [s / max_score for s in scores]
        return scores


class Retriever:
    """
    IVF 벡터 검색 + BM25 독립 키워드 검색을 병렬로 돌린 뒤 hybrid reranking.
    임베딩 모델이 못 잡는 키워드 매칭 문서를 BM25가 보완.
    비율은 7:3 (semantic:keyword). 5:5는 키워드에 너무 끌려감.
    """

    def __init__(
        self,
        index: IVFIndex,
        embedding_engine: EmbeddingEngine,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3,
    ):
        self.index = index
        self.embedding_engine = embedding_engine
        self.semantic_weight = semantic_weight
        self.keyword_weight = keyword_weight
        self.bm25 = BM25Scorer()

    _OVERVIEW_QUERY_HINTS = {
        "개요", "설명", "간략", "간략히", "간단", "간단히", "소개", "기본", "핵심", "무엇"
    }
    _GENERIC_QUERY_TOKENS = {
        "개요", "설명", "간략", "간략히", "간단", "간단히", "소개", "기본", "핵심",
        "무엇", "대해", "대해서", "관해", "알려줘", "설명해봐", "해봐",
    }
    _ENTITY_TERMS = {
        "openshift": {"오픈시프트", "openshift", "ocp"},
        "kubernetes": {"쿠버네티스", "kubernetes", "k8s"},
    }
    _SOURCE_PRIOR = {
        "openshift": ("ocp-basics", "ocp_architecture_overview", "ocp-core-concepts-ko"),
        "kubernetes": ("k8s_overview", "k8s_components"),
    }
    _INTRO_MARKERS = (
        "기본 개념", "핵심 개념", "overview", "introduction", "란?", "란",
        "what is", "architecture overview",
    )

    def _detect_primary_entity(self, query_tokens: set[str]) -> str | None:
        for entity, terms in self._ENTITY_TERMS.items():
            if query_tokens & terms:
                return entity
        return None

    def _is_overview_query(self, query: str) -> tuple[bool, str | None]:
        query_tokens = set(self.bm25._tokenize(query))
        entity = self._detect_primary_entity(query_tokens)
        has_overview_hint = bool(query_tokens & self._OVERVIEW_QUERY_HINTS)
        generic_tokens = set(self._GENERIC_QUERY_TOKENS)
        if entity:
            generic_tokens |= self._ENTITY_TERMS[entity]
        informative_tokens = query_tokens - generic_tokens
        return has_overview_hint and len(informative_tokens) <= 1, entity

    def _overview_boost(self, query: str, candidate: SearchResult) -> float:
        is_overview_query, entity = self._is_overview_query(query)
        if not is_overview_query:
            return 0.0

        source = candidate.metadata.get("source", "").lower()
        text_head = candidate.text[:400].lower()
        boost = 0.0

        if candidate.metadata.get("chunk_index") == 0:
            boost += 0.04

        if any(marker in source or marker in text_head for marker in self._INTRO_MARKERS):
            boost += 0.08

        if entity:
            if any(term in source or term in text_head for term in self._ENTITY_TERMS[entity]):
                boost += 0.06
            if any(hint in source for hint in self._SOURCE_PRIOR[entity]):
                boost += 0.18

        return boost

    def retrieve(self, query: str, top_k: int = TOP_K) -> list[RankedResult]:
        """쿼리로 관련 문서 검색 + 리랭킹

        경로 1: IVF 벡터 검색 (top_k*3개)
        경로 2: BM25 전체 코퍼스 키워드 검색 (top_k*2개) — IVF에서 못 잡는 문서 보완
        두 결과를 합쳐서 hybrid scoring 후 최종 top_k 반환
        """
        # 1. 쿼리 임베딩
        query_vector = self.embedding_engine.embed(query)

        # 2. 경로 1: IVF 벡터 검색
        candidates = self.index.search(query_vector, top_k=top_k * 3)

        # 3. 경로 2: BM25 전체 코퍼스 검색 (IVF에서 못 잡는 키워드 매칭 문서 보완)
        bm25_hits = self.bm25.search_corpus(query, top_k=top_k * 2)

        # IVF 결과가 없고 BM25도 없으면 빈 결과
        if not candidates and not bm25_hits:
            return []

        # 4. BM25 전용 후보를 IVF 결과에 합치기 (중복 제거)
        seen_chunk_ids = {c.chunk_id for c in candidates}
        for doc_idx, _ in bm25_hits:
            doc = self.index.documents[doc_idx]
            if doc["chunk_id"] not in seen_chunk_ids:
                # BM25로만 찾은 문서 → semantic score 계산
                vec = self.index.vectors[doc_idx].astype(np.float32)
                q = query_vector.flatten().astype(np.float32)
                norm_v = np.linalg.norm(vec)
                norm_q = np.linalg.norm(q)
                sem_score = float(np.dot(vec, q) / (norm_v * norm_q)) if norm_v > 0 and norm_q > 0 else 0.0
                candidates.append(SearchResult(
                    chunk_id=doc["chunk_id"],
                    text=doc["text"],
                    score=sem_score,
                    metadata=doc.get("metadata", {}),
                ))
                seen_chunk_ids.add(doc["chunk_id"])

        # 5. 합쳐진 전체 후보에 BM25 reranking 스코어 계산
        candidate_texts = [c.text for c in candidates]
        keyword_scores = self.bm25.score(query, candidate_texts)

        # 6. hybrid scoring으로 리랭킹
        ranked = []
        for i, candidate in enumerate(candidates):
            combined_score = (
                self.semantic_weight * candidate.score
                + self.keyword_weight * keyword_scores[i]
            )
            combined_score += self._overview_boost(query, candidate)
            ranked.append(RankedResult(
                chunk_id=candidate.chunk_id,
                text=candidate.text,
                score=combined_score,
                semantic_score=candidate.score,
                keyword_score=keyword_scores[i],
                metadata=candidate.metadata,
            ))

        ranked.sort(key=lambda x: x.score, reverse=True)
        top_results = ranked[:top_k]

        # 7. 인접 청크 확장: 검색된 청크의 앞뒤 청크를 포함시켜 문맥 보완
        return self._expand_adjacent_chunks(top_results)

    def _expand_adjacent_chunks(self, results: list[RankedResult], window: int = 2) -> list[RankedResult]:
        """검색된 청크의 인접 청크(같은 문서, ±window)를 텍스트에 병합.

        chunk_id 형식: "source::N" (예: "ocp-image-pull-troubleshooting-ko.md::0")
        같은 source의 N-window ~ N+window 청크를 찾아서 텍스트를 합침.
        이렇게 하면 chunk 0만 잡혀도 chunk 1,2의 해결 방법까지 LLM이 볼 수 있음.
        """
        if not self.index.documents:
            return results

        # chunk_id → index 매핑 (최초 1회 구축)
        if not hasattr(self, '_chunk_id_to_idx'):
            self._chunk_id_to_idx = {}
            for idx, doc in enumerate(self.index.documents):
                self._chunk_id_to_idx[doc["chunk_id"]] = idx

        expanded = []
        for r in results:
            # chunk_id 파싱: "source::N"
            if "::" not in r.chunk_id:
                expanded.append(r)
                continue

            source, chunk_num_str = r.chunk_id.rsplit("::", 1)
            try:
                chunk_num = int(chunk_num_str)
            except ValueError:
                expanded.append(r)
                continue

            # 인접 청크 수집 (현재 청크 포함)
            texts = []
            for offset in range(-window, window + 1):
                adj_id = f"{source}::{chunk_num + offset}"
                adj_idx = self._chunk_id_to_idx.get(adj_id)
                if adj_idx is not None:
                    texts.append(self.index.documents[adj_idx]["text"])

            # 병합된 텍스트로 결과 교체
            merged_text = "\n\n".join(texts)
            expanded.append(RankedResult(
                chunk_id=r.chunk_id,
                text=merged_text,
                score=r.score,
                semantic_score=r.semantic_score,
                keyword_score=r.keyword_score,
                metadata=r.metadata,
            ))

        return expanded

    def build_context(self, results: list[RankedResult], max_chars: int = 4000) -> str:
        """검색 결과를 LLM에 전달할 context 문자열로 구성 (길이 제한)"""
        if not results:
            return "관련 문서를 찾지 못했습니다."

        context_parts = []
        total_len = 0
        for i, r in enumerate(results, 1):
            source = r.metadata.get("source", "unknown")
            # 출처명을 제목처럼 써야 LLM이 답변에서 구체적 문서명을 인용함
            # 이전에 "[문서 1] (출처: xxx)" 했더니 LLM이 "문서 1에 따르면"으로만 답변해서 변경
            part = f"[{source}]\n{r.text}"
            if total_len + len(part) > max_chars:
                # 남은 공간만큼만 추가
                remaining = max_chars - total_len
                if remaining > 100:
                    context_parts.append(part[:remaining] + "...")
                break
            context_parts.append(part)
            total_len += len(part) + 7  # "\n\n---\n\n"
        return "\n\n---\n\n".join(context_parts)
