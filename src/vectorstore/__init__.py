"""
IVF 벡터 인덱스. FAISS 안 쓰고 numpy로 직접 구현.
K-Means로 클러스터 나눈 뒤, 검색할 때는 가까운 클러스터 몇 개만 탐색해서 속도 확보.
"""
import os
import json
import numpy as np
from dataclasses import dataclass
from typing import Optional

from src.config import INDEX_DIR, IVF_N_CLUSTERS, IVF_N_PROBE, TOP_K


@dataclass
class SearchResult:
    """검색 결과 하나"""
    chunk_id: str
    text: str
    score: float
    metadata: dict


class IVFIndex:
    """IVF(Inverted File Index) 기반 벡터 인덱스

    직접 구현한 K-Means + Inverted List 구조:
    - build(): 벡터들을 K-Means 클러스터링하여 인덱스 구축
    - search(): 쿼리 벡터로 가장 유사한 문서 검색
    - save()/load(): 인덱스를 디스크에 저장/로드
    """

    def __init__(self, dim: int, n_clusters: int = IVF_N_CLUSTERS, n_probe: int = IVF_N_PROBE):
        self.dim = dim
        self.n_clusters = n_clusters
        # n_probe: 검색 시 탐색할 클러스터 수. 높이면 정확도↑ 속도↓
        # 처음에 1로 했다가 경계에 있는 문서를 못 찾는 경우가 있어서 3으로 올림
        self.n_probe = n_probe

        # 클러스터 중심 벡터 (n_clusters x dim)
        self.centroids: Optional[np.ndarray] = None
        # 클러스터별 벡터 목록 (inverted list)
        self.inverted_lists: dict[int, list[int]] = {}
        # 전체 벡터 저장소
        self.vectors: Optional[np.ndarray] = None
        # 메타데이터 (chunk_id, text 등)
        self.documents: list[dict] = []
        self._is_built = False

    def add_documents(self, vectors: np.ndarray, documents: list[dict]):
        """문서 벡터와 메타데이터 추가

        Args:
            vectors: (N, dim) 벡터 배열
            documents: [{"chunk_id": ..., "text": ..., "metadata": ...}, ...]
        """
        if self.vectors is None:
            self.vectors = vectors.astype(np.float32)
            self.documents = documents
        else:
            self.vectors = np.vstack([self.vectors, vectors.astype(np.float32)])
            self.documents.extend(documents)
        self._is_built = False

    def build(self, max_iter: int = 20):
        """K-Means 클러스터링으로 IVF 인덱스 구축

        직접 구현한 K-Means:
        1. 랜덤 초기 중심점 선택
        2. 각 벡터를 가장 가까운 중심점에 할당
        3. 중심점을 해당 클러스터 벡터들의 평균으로 업데이트
        4. 수렴할 때까지 반복
        """
        if self.vectors is None or len(self.vectors) == 0:
            raise ValueError("인덱스에 벡터가 없습니다. add_documents()를 먼저 호출하세요.")

        n_vectors = len(self.vectors)
        actual_clusters = min(self.n_clusters, n_vectors)

        # 벡터 정규화 (cosine similarity를 위해)
        norms = np.linalg.norm(self.vectors, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1, norms)
        normalized = self.vectors / norms

        # K-Means: 랜덤 초기 중심점
        # seed 고정 안 하면 빌드할 때마다 클러스터 배치 달라져서 검색 결과가 흔들림
        rng = np.random.default_rng(42)
        indices = rng.choice(n_vectors, size=actual_clusters, replace=False)
        self.centroids = normalized[indices].copy()

        assignments = np.zeros(n_vectors, dtype=np.int32)

        for _ in range(max_iter):
            # 각 벡터를 가장 가까운 중심점에 할당
            # cosine similarity = dot product (정규화된 벡터)
            similarities = normalized @ self.centroids.T  # (N, K)
            new_assignments = np.argmax(similarities, axis=1)

            # 수렴 체크
            if np.array_equal(assignments, new_assignments):
                break
            assignments = new_assignments

            # 중심점 업데이트
            for k in range(actual_clusters):
                mask = assignments == k
                if np.any(mask):
                    centroid = normalized[mask].mean(axis=0)
                    norm = np.linalg.norm(centroid)
                    if norm > 0:
                        self.centroids[k] = centroid / norm

        # Inverted list 구축
        self.inverted_lists = {}
        for idx, cluster_id in enumerate(assignments):
            cluster_id = int(cluster_id)
            if cluster_id not in self.inverted_lists:
                self.inverted_lists[cluster_id] = []
            self.inverted_lists[cluster_id].append(idx)

        self._is_built = True

    def search(self, query_vector: np.ndarray, top_k: int = TOP_K) -> list[SearchResult]:
        """쿼리 벡터로 가장 유사한 문서 검색

        과정:
        1. 쿼리 벡터와 가장 가까운 n_probe개 클러스터 찾기
        2. 해당 클러스터의 벡터들만 대상으로 cosine similarity 계산
        3. Top-K 결과 반환
        """
        if not self._is_built:
            raise ValueError("인덱스가 빌드되지 않았습니다. build()를 먼저 호출하세요.")

        # 쿼리 벡터 정규화
        query = query_vector.astype(np.float32).flatten()
        norm = np.linalg.norm(query)
        if norm > 0:
            query = query / norm

        # 1. 가장 가까운 n_probe개 클러스터 찾기
        centroid_sims = self.centroids @ query  # (K,)
        probe_clusters = np.argsort(centroid_sims)[-self.n_probe:][::-1]

        # 2. 해당 클러스터 내 벡터들만 검색
        candidate_indices = []
        for cluster_id in probe_clusters:
            cluster_id = int(cluster_id)
            if cluster_id in self.inverted_lists:
                candidate_indices.extend(self.inverted_lists[cluster_id])

        if not candidate_indices:
            return []

        # n_probe > 1이면 클러스터 경계에 있는 벡터가 중복 포함될 수 있음
        candidate_indices = list(set(candidate_indices))
        candidate_vectors = self.vectors[candidate_indices]

        # 정규화
        norms = np.linalg.norm(candidate_vectors, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1, norms)
        candidate_normalized = candidate_vectors / norms

        # 3. cosine similarity 계산
        similarities = candidate_normalized @ query  # (M,)

        # Top-K 선택
        k = min(top_k, len(similarities))
        top_indices = np.argsort(similarities)[-k:][::-1]

        results = []
        for idx in top_indices:
            doc_idx = candidate_indices[idx]
            doc = self.documents[doc_idx]
            results.append(SearchResult(
                chunk_id=doc["chunk_id"],
                text=doc["text"],
                score=float(similarities[idx]),
                metadata=doc.get("metadata", {}),
            ))

        return results

    def brute_force_search(self, query_vector: np.ndarray, top_k: int = TOP_K) -> list[SearchResult]:
        """전수검색. IVF 결과 검증할 때 비교용으로 만들어둠. 실서비스에선 안 씀."""
        if self.vectors is None or len(self.vectors) == 0:
            return []

        query = query_vector.astype(np.float32).flatten()
        norm = np.linalg.norm(query)
        if norm > 0:
            query = query / norm

        norms = np.linalg.norm(self.vectors, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1, norms)
        normalized = self.vectors / norms

        similarities = normalized @ query
        k = min(top_k, len(similarities))
        top_indices = np.argsort(similarities)[-k:][::-1]

        results = []
        for idx in top_indices:
            doc = self.documents[idx]
            results.append(SearchResult(
                chunk_id=doc["chunk_id"],
                text=doc["text"],
                score=float(similarities[idx]),
                metadata=doc.get("metadata", {}),
            ))
        return results

    def save(self, dirpath: str = INDEX_DIR):
        """인덱스를 디스크에 저장"""
        os.makedirs(dirpath, exist_ok=True)

        # 벡터 저장
        np.save(os.path.join(dirpath, "vectors.npy"), self.vectors)
        # 중심점 저장
        if self.centroids is not None:
            np.save(os.path.join(dirpath, "centroids.npy"), self.centroids)

        # 메타데이터 저장
        meta = {
            "documents": self.documents,
            "inverted_lists": {str(k): v for k, v in self.inverted_lists.items()},
            "dim": self.dim,
            "n_clusters": self.n_clusters,
            "n_probe": self.n_probe,
        }
        with open(os.path.join(dirpath, "index_meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, dirpath: str = INDEX_DIR) -> "IVFIndex":
        """디스크에서 인덱스 로드"""
        with open(os.path.join(dirpath, "index_meta.json"), "r", encoding="utf-8") as f:
            meta = json.load(f)

        index = cls(
            dim=meta["dim"],
            n_clusters=meta["n_clusters"],
            n_probe=meta["n_probe"],
        )
        index.vectors = np.load(os.path.join(dirpath, "vectors.npy"))
        centroids_path = os.path.join(dirpath, "centroids.npy")
        if os.path.exists(centroids_path):
            index.centroids = np.load(centroids_path)
        index.documents = meta["documents"]
        index.inverted_lists = {int(k): v for k, v in meta["inverted_lists"].items()}
        index._is_built = True
        return index

    def stats(self) -> dict:
        """인덱스 상태 정보"""
        cluster_sizes = {k: len(v) for k, v in self.inverted_lists.items()}
        return {
            "total_vectors": len(self.vectors) if self.vectors is not None else 0,
            "n_clusters": self.n_clusters,
            "n_probe": self.n_probe,
            "is_built": self._is_built,
            "cluster_sizes": cluster_sizes,
        }
