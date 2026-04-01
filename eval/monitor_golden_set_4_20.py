from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Monitor the enterprise-4.20 Golden Set benchmark state.")
    parser.add_argument(
        "--db",
        type=Path,
        default=REPO_ROOT / "indexes" / "golden-set-4.20" / ".data" / "opendocuments.db",
    )
    parser.add_argument(
        "--results",
        type=Path,
        default=REPO_ROOT / "data" / "manifests" / "generated" / "golden_set_4_20_results.jsonl",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=REPO_ROOT / "data" / "manifests" / "generated" / "golden_set_4_20_report.json",
    )
    parser.add_argument(
        "--failures",
        type=Path,
        default=REPO_ROOT / "data" / "manifests" / "generated" / "golden_set_4_20_failures.json",
    )
    parser.add_argument(
        "--sample",
        type=Path,
        default=REPO_ROOT / "data" / "manifests" / "generated" / "golden_set_4_20_sample.json",
    )
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def file_meta(path: Path) -> dict[str, object]:
    if not path.exists():
        return {"exists": False}
    stat = path.stat()
    return {
        "exists": True,
        "bytes": stat.st_size,
        "last_modified_utc": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
    }


def main() -> None:
    args = parse_args()
    summary: dict[str, object] = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "db_path": str(args.db),
        "db_exists": args.db.exists(),
        "statuses": {},
        "error_messages": [],
        "artifacts": {
            "results": file_meta(args.results),
            "report": file_meta(args.report),
            "failures": file_meta(args.failures),
            "sample": file_meta(args.sample),
        },
    }

    if args.db.exists():
        conn = sqlite3.connect(args.db)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        statuses = {
            row["status"]: row["cnt"]
            for row in cur.execute(
                "select status, count(*) as cnt from documents group by status order by status"
            )
        }
        summary["statuses"] = statuses
        summary["indexed_count"] = statuses.get("indexed", 0)
        summary["pending_count"] = statuses.get("pending", 0)
        summary["processing_count"] = statuses.get("processing", 0)
        summary["error_count"] = statuses.get("error", 0)

        summary["error_messages"] = [
            {"error_message": row["error_message"], "count": row["cnt"]}
            for row in cur.execute(
                """
                select error_message, count(*) as cnt
                from documents
                where error_message is not null and error_message <> ''
                group by error_message
                order by cnt desc, error_message asc
                limit 10
                """
            )
        ]

        summary["stale_pending"] = [
            dict(row)
            for row in cur.execute(
                """
                select title, source_path, status, updated_at, error_message
                from documents
                where status in ('pending', 'processing')
                order by updated_at asc
                limit 10
                """
            )
        ]

        conn.close()

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
