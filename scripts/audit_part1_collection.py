from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag_part1.collection_audit import write_collection_audit_report
from ocp_rag_part1.settings import load_settings


def main() -> int:
    settings = load_settings(ROOT)
    report = write_collection_audit_report(settings)
    summary = report["summary"]
    print(f"wrote collection audit: {settings.collection_audit_report_path}")
    print(f"book_count={report['book_count']}")
    print(f"collection_status_counts={summary['collection_status_counts']}")
    print(f"vendor_fallback_books={len(summary['vendor_fallback_books'])}")
    print(f"translate_priority_books={summary['translate_priority_books']}")
    print(f"exclude_default_books={len(summary['exclude_default_books'])}")
    print(f"collector_misroute_books={summary['collector_misroute_books']}")
    print(f"missing_raw_html_books={summary['missing_raw_html_books']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
