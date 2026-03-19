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

    def _tokenize(self, text: str) -> list[str]:
        """간단한 토크나이저. 형태소 분석기 쓰면 좋겠지만 의존성 늘리기 싫어서 정규식으로 처리"""
        # TODO: konlpy 같은 거 넣으면 한국어 검색 정확도 올라갈 듯
        text = text.lower()
        tokens = re.findall(r"[a-z0-9]+|[가-힣]+", text)
        return tokens

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
            ranked.append(RankedResult(
                chunk_id=candidate.chunk_id,
                text=candidate.text,
                score=combined_score,
                semantic_score=candidate.score,
                keyword_score=keyword_scores[i],
                metadata=candidate.metadata,
            ))

        ranked.sort(key=lambda x: x.score, reverse=True)
        return ranked[:top_k]

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
