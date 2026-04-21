from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.config.settings import load_settings
from play_book_studio.config.validation import read_jsonl
from play_book_studio.ingestion.chunking import chunk_sections
from play_book_studio.ingestion.embedding import EmbeddingClient
from play_book_studio.ingestion.playbook_materialization import (
    project_playbook_payload_sections,
)
from play_book_studio.ingestion.qdrant_store import ensure_collection, upsert_chunks


REPORT_PATH = ROOT / "reports" / "build_logs" / "active_gold_corpus_rebuild_report.json"


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _load_playbook_rows(settings) -> list[dict]:
    rows: list[dict] = []
    for row in read_jsonl(settings.retrieval_playbook_documents_path):
        slug = str(row.get("book_slug") or "").strip()
        if not slug:
            continue
        rows.append(dict(row))
    if not rows:
        raise RuntimeError(f"playbook documents are empty: {settings.retrieval_playbook_documents_path}")
    return rows


def _build_bm25_rows(chunks) -> list[dict]:
    return [
        {
            "chunk_id": chunk.chunk_id,
            "book_slug": chunk.book_slug,
            "chapter": chunk.chapter,
            "section": chunk.section,
            "anchor": chunk.anchor,
            "source_url": chunk.source_url,
            "viewer_path": chunk.viewer_path,
            "text": chunk.text,
            "section_path": list(chunk.section_path),
            "chunk_type": chunk.chunk_type,
            "source_id": chunk.source_id,
            "source_lane": chunk.source_lane,
            "source_type": chunk.source_type,
            "source_collection": chunk.source_collection,
            "product": chunk.product,
            "version": chunk.version,
            "locale": chunk.locale,
            "translation_status": chunk.translation_status,
            "review_status": chunk.review_status,
            "trust_score": chunk.trust_score,
            "semantic_role": "procedure"
            if chunk.chunk_type in {"procedure", "command"}
            else ("concept" if chunk.chunk_type == "concept" else "reference"),
            "cli_commands": list(chunk.cli_commands),
            "error_strings": list(chunk.error_strings),
            "k8s_objects": list(chunk.k8s_objects),
            "operator_names": list(chunk.operator_names),
            "verification_hints": list(chunk.verification_hints),
        }
        for chunk in chunks
    ]


def main() -> int:
    settings = load_settings(ROOT)
    rows = _load_playbook_rows(settings)
    print(f"[playbooks] count={len(rows)}", flush=True)

    sections = []
    for index, row in enumerate(rows, start=1):
        projected = project_playbook_payload_sections(row)
        sections.extend(projected)
        print(
            f"[sections {index}/{len(rows)}] {row.get('book_slug')} -> {len(projected)}",
            flush=True,
        )

    chunks = chunk_sections(sections, settings)
    chunk_rows = [chunk.to_dict() for chunk in chunks]
    bm25_rows = _build_bm25_rows(chunks)

    settings.gold_corpus_ko_dir.mkdir(parents=True, exist_ok=True)
    chunks_path = settings.gold_corpus_ko_dir / "chunks.jsonl"
    bm25_path = settings.gold_corpus_ko_dir / "bm25_corpus.jsonl"
    _write_jsonl(chunks_path, chunk_rows)
    _write_jsonl(bm25_path, bm25_rows)
    print(f"[chunks] total={len(chunks)}", flush=True)

    client = EmbeddingClient(settings)
    vectors = client.embed_texts(
        (chunk.text for chunk in chunks),
        progress_callback=lambda done, total: print(f"[embed {done}/{total}]", flush=True),
    )
    ensure_collection(settings)
    upserted = upsert_chunks(
        settings,
        chunks,
        vectors,
        progress_callback=lambda done, total: print(f"[qdrant {done}/{total}]", flush=True),
    )

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "playbook_count": len(rows),
        "section_count": len(sections),
        "chunk_count": len(chunks),
        "qdrant_upserted_count": upserted,
        "chunks_path": str(chunks_path),
        "bm25_corpus_path": str(bm25_path),
        "qdrant_url": settings.qdrant_url,
        "qdrant_collection": settings.qdrant_collection,
    }
    REPORT_PATH.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    from play_book_studio.execution_guard import run_guarded_script

    raise SystemExit(run_guarded_script(main, __file__, launcher_hint="scripts/codex_python.ps1"))
