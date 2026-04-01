from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class VectorRecord:
    chunk_id: str
    document_id: str
    document_path: str
    section_id: str
    section_title: str
    viewer_url: str
    embedding: tuple[float, ...]
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["embedding"] = list(self.embedding)
        return payload


@dataclass(frozen=True)
class VectorSearchResult:
    rank: int
    score: float
    chunk_id: str
    document_id: str
    document_path: str
    section_id: str
    section_title: str
    viewer_url: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _dot(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    return sum(a * b for a, b in zip(left, right, strict=False))


def _norm(vector: tuple[float, ...]) -> float:
    return math.sqrt(sum(value * value for value in vector))


def cosine_similarity(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    if len(left) != len(right):
        raise ValueError(
            f"Vector dimension mismatch: left={len(left)} right={len(right)}"
        )
    left_norm = _norm(left)
    right_norm = _norm(right)
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return _dot(left, right) / (left_norm * right_norm)


class VectorIndex:
    def __init__(self, *, dimensions: int) -> None:
        if dimensions <= 0:
            raise ValueError("dimensions must be positive")
        self.dimensions = dimensions
        self._records: list[VectorRecord] = []

    @property
    def size(self) -> int:
        return len(self._records)

    def add(self, record: VectorRecord) -> None:
        if len(record.embedding) != self.dimensions:
            raise ValueError(
                f"Record dimension mismatch: expected {self.dimensions}, got {len(record.embedding)}"
            )
        self._records.append(record)

    def extend(self, records: list[VectorRecord]) -> None:
        for record in records:
            self.add(record)

    def search(
        self, query_vector: tuple[float, ...], *, top_k: int = 5
    ) -> list[VectorSearchResult]:
        if len(query_vector) != self.dimensions:
            raise ValueError(
                f"Query dimension mismatch: expected {self.dimensions}, got {len(query_vector)}"
            )
        ranked = sorted(
            (
                (
                    cosine_similarity(query_vector, record.embedding),
                    record,
                )
                for record in self._records
            ),
            key=lambda item: item[0],
            reverse=True,
        )
        return [
            VectorSearchResult(
                rank=index,
                score=round(score, 6),
                chunk_id=record.chunk_id,
                document_id=record.document_id,
                document_path=record.document_path,
                section_id=record.section_id,
                section_title=record.section_title,
                viewer_url=record.viewer_url,
                metadata=dict(record.metadata),
            )
            for index, (score, record) in enumerate(ranked[:top_k], start=1)
        ]

    def to_dict(self) -> dict[str, Any]:
        return {
            "dimensions": self.dimensions,
            "record_count": self.size,
            "records": [record.to_dict() for record in self._records],
        }

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self.to_dict(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path: Path) -> "VectorIndex":
        payload = json.loads(path.read_text(encoding="utf-8"))
        index = cls(dimensions=int(payload["dimensions"]))
        for item in payload.get("records", []):
            index.add(
                VectorRecord(
                    chunk_id=str(item["chunk_id"]),
                    document_id=str(item["document_id"]),
                    document_path=str(item["document_path"]),
                    section_id=str(item["section_id"]),
                    section_title=str(item["section_title"]),
                    viewer_url=str(item["viewer_url"]),
                    embedding=tuple(float(v) for v in item["embedding"]),
                    metadata=dict(item.get("metadata", {})),
                )
            )
        return index
