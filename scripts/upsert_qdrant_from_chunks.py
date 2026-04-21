from __future__ import annotations

import argparse
import json
import sys
from dataclasses import fields
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.config.settings import load_settings
from play_book_studio.ingestion.embedding import EmbeddingClient
from play_book_studio.ingestion.models import ChunkRecord
from play_book_studio.ingestion.qdrant_store import ensure_collection, upsert_chunks


REPORT_PATH = ROOT / "reports" / "build_logs" / "qdrant_upsert_from_chunks_report.json"


def _iter_chunk_batches(path: Path, batch_size: int):
    allowed = {field.name for field in fields(ChunkRecord)}
    batch: list[ChunkRecord] = []
    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            row = json.loads(line)
            payload = {key: value for key, value in row.items() if key in allowed}
            payload["section_path"] = tuple(payload.get("section_path", []))
            payload["access_groups"] = tuple(payload.get("access_groups", []))
            payload["cli_commands"] = tuple(payload.get("cli_commands", []))
            payload["error_strings"] = tuple(payload.get("error_strings", []))
            payload["k8s_objects"] = tuple(payload.get("k8s_objects", []))
            payload["operator_names"] = tuple(payload.get("operator_names", []))
            payload["verification_hints"] = tuple(payload.get("verification_hints", []))
            batch.append(ChunkRecord(**payload))
            if len(batch) >= batch_size:
                yield batch
                batch = []
    if batch:
        yield batch


def _count_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chunks-path", type=Path, required=True)
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--qdrant-url", type=str, default="")
    parser.add_argument("--qdrant-collection", type=str, default="")
    parser.add_argument("--recreate-collection", action="store_true")
    args = parser.parse_args()

    settings = load_settings(ROOT)
    if args.qdrant_url.strip():
        settings.qdrant_url = args.qdrant_url.strip().rstrip("/")
    if args.qdrant_collection.strip():
        settings.qdrant_collection = args.qdrant_collection.strip()
    if args.recreate_collection:
        settings.qdrant_recreate_collection = True
    chunks_path = args.chunks_path.resolve()
    if not chunks_path.exists():
        raise FileNotFoundError(f"missing chunks path: {chunks_path}")

    total_rows = _count_rows(chunks_path)
    total_batches = (total_rows + args.batch_size - 1) // args.batch_size
    client = EmbeddingClient(settings)

    ensure_collection(settings)

    processed_rows = 0
    upserted_rows = 0
    for batch_index, chunk_batch in enumerate(
        _iter_chunk_batches(chunks_path, args.batch_size),
        start=1,
    ):
        vectors = client.embed_texts(chunk.text for chunk in chunk_batch)
        upserted_rows += upsert_chunks(settings, chunk_batch, vectors)
        processed_rows += len(chunk_batch)
        print(
            json.dumps(
                {
                    "stage": "qdrant_upsert",
                    "batch": batch_index,
                    "total_batches": total_batches,
                    "processed_rows": processed_rows,
                    "total_rows": total_rows,
                },
                ensure_ascii=False,
            ),
            flush=True,
        )

    report = {
        "chunks_path": str(chunks_path),
        "chunk_count": total_rows,
        "batch_size": args.batch_size,
        "qdrant_url": settings.qdrant_url,
        "qdrant_collection": settings.qdrant_collection,
        "upserted_count": upserted_rows,
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    from play_book_studio.execution_guard import run_guarded_script

    raise SystemExit(run_guarded_script(main, __file__, launcher_hint="scripts/codex_python.ps1"))
