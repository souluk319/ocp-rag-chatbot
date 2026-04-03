from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag_part1.language_policy import write_language_policy_report
from ocp_rag_part1.settings import load_settings


def main() -> int:
    settings = load_settings(ROOT)
    report = write_language_policy_report(settings)
    summary = report["summary"]
    print(f"book_count={report['book_count']}")
    print(f"translate_priority_count={len(summary['translate_priority_books'])}")
    print(f"exclude_default_count={len(summary['exclude_default_books'])}")
    print(f"language_policy_report={settings.language_policy_report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
