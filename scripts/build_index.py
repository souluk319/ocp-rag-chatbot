"""문서 인덱싱 스크립트

data/sanitized_raw/ 디렉토리의 정제본을 청킹 → 임베딩 → IVF 인덱스 구축 → 저장
"""
import sys
import os
import time

# 프로젝트 루트를 path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import DATA_CORPUS_DIR, INDEX_DIR, EMBEDDING_DIM, IVF_N_CLUSTERS
from src.chunker import Chunker
from src.embedding import EmbeddingEngine
from src.vectorstore import IVFIndex


def build_index():
    print("=" * 60)
    print("OCP RAG Chatbot - 문서 인덱싱")
    print("=" * 60)

    # 1. 문서 청킹
    print(f"\n[1/4] 문서 청킹 중... (소스: {DATA_CORPUS_DIR})")
    chunker = Chunker()
    chunks = chunker.chunk_directory(DATA_CORPUS_DIR)
    print(f"  -> {len(chunks)}개 청크 생성")

    if not chunks:
        print("\n문서가 없습니다. data/sanitized_raw/ 디렉토리를 확인하세요.")
        print("필요하면 먼저 python3 scripts/sanitize_corpus.py 를 실행하세요.")
        print("지원 형식: .txt, .md, .pdf, .docx, .pptx")
        return

    # 2. 임베딩 생성
    print(f"\n[2/4] 임베딩 생성 중... (모델: {EMBEDDING_DIM}차원)")
    engine = EmbeddingEngine()
    texts = [c.text for c in chunks]

    start = time.time()
    vectors = engine.embed_batch(texts)
    elapsed = time.time() - start
    print(f"  -> {len(vectors)}개 벡터 생성 ({elapsed:.1f}초)")

    # 3. IVF 인덱스 구축
    n_clusters = min(IVF_N_CLUSTERS, len(chunks))
    print(f"\n[3/4] IVF 인덱스 구축 중... ({n_clusters}개 클러스터)")
    index = IVFIndex(dim=EMBEDDING_DIM, n_clusters=n_clusters)

    documents = [
        {
            "chunk_id": c.chunk_id,
            "text": c.text,
            "metadata": c.metadata,
        }
        for c in chunks
    ]
    index.add_documents(vectors, documents)

    start = time.time()
    index.build()
    elapsed = time.time() - start
    print(f"  -> 인덱스 구축 완료 ({elapsed:.1f}초)")

    # 4. 저장
    print(f"\n[4/4] 인덱스 저장 중... ({INDEX_DIR})")
    index.save()
    print(f"  -> 저장 완료")

    # 요약
    stats = index.stats()
    print(f"\n{'=' * 60}")
    print(f"인덱싱 완료!")
    print(f"  총 벡터 수: {stats['total_vectors']}")
    print(f"  클러스터 수: {stats['n_clusters']}")
    print(f"  클러스터별 벡터 수: {dict(stats['cluster_sizes'])}")
    print(f"  임베딩 캐시: {engine.cache_stats()}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    build_index()
