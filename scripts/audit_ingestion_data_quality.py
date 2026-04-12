# 정규화/청킹 결과 품질을 점검해 data quality 리포트를 만드는 스크립트.
# 코퍼스 품질 문제가 의심될 때 ingestion 산출물을 빠르게 감사할 때 쓴다.
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.ingestion.audit import build_data_quality_report
from play_book_studio.config.settings import load_settings


def main() -> int:
    settings = load_settings(ROOT)
    report = build_data_quality_report(settings)
    output_path = settings.corpus_dir / "data_quality_report.json"
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote data quality report: {output_path}")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    from play_book_studio.execution_guard import run_guarded_script

    raise SystemExit(run_guarded_script(main, __file__, launcher_hint="scripts/codex_python.ps1"))
