# approved manifest 기준으로 collect/normalize/chunk/embed/qdrant 전체를 실행한다.
# 표준 ingestion 진입점은 full run 한 경로만 허용한다.
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.ingestion.pipeline import run_ingestion_pipeline
from play_book_studio.config.settings import load_settings


def main() -> int:
    settings = load_settings(ROOT)
    log = run_ingestion_pipeline(
        settings,
        refresh_manifest=False,
        collect_subset="all",
        process_subset="all",
        collect_limit=None,
        process_limit=None,
        force_collect=False,
        skip_embeddings=False,
        skip_qdrant=False,
    )
    print(f"manifest_count={log.manifest_count}")
    print(f"collected_count={log.collected_count}")
    print(f"normalized_count={log.normalized_count}")
    print(f"chunk_count={log.chunk_count}")
    print(f"embedded_count={log.embedded_count}")
    print(f"qdrant_upserted_count={log.qdrant_upserted_count}")
    print(f"errors={len(log.errors)}")
    if log.errors:
        for error in log.errors:
            print(f"[{error['stage']}] {error['source']}: {error['message']}")
    return 0


if __name__ == "__main__":
    from play_book_studio.execution_guard import run_guarded_script

    raise SystemExit(run_guarded_script(main, __file__, launcher_hint="scripts/codex_python.ps1"))
