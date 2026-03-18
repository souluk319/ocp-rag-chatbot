"""
검색 + 리랭킹. IVF에서 후보를 넉넉히 뽑고(top_k*3),
semantic score와 BM25 keyword score를 섞어서 최종 순위 결정.
"""
import re
import math
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
    """BM25 스타일 키워드 매칭 스코어러

    문서 컬렉션 전체가 아닌, 검색된 후보군 내에서의 키워드 관련성을 계산.
    IDF는 후보군 기준으로 계산하여 희귀 키워드에 더 높은 가중치 부여.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b

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
    semantic만으로는 키워드 매칭이 약해서 BM25를 30% 섞음.
    비율은 몇 번 테스트해보고 7:3이 제일 나았음 (5:5는 키워드에 너무 끌려감).
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
        """쿼리로 관련 문서 검색 + 리랭킹"""
        # 1. 쿼리 임베딩
        query_vector = self.embedding_engine.embed(query)

        # 2. IVF 인덱스에서 후보 검색 (over-retrieve)
        candidates = self.index.search(query_vector, top_k=top_k * 3)
        if not candidates:
            return []

        # 3. BM25 키워드 스코어 계산
        candidate_texts = [c.text for c in candidates]
        keyword_scores = self.bm25.score(query, candidate_texts)

        # 4. 결합 스코어로 리랭킹
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

        # 결합 스코어 기준 정렬
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
