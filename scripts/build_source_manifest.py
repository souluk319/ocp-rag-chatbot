from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag.ingest.pipeline import ensure_manifest
from ocp_rag.shared.settings import load_settings


def main() -> int:
    settings = load_settings(ROOT)
    entries = ensure_manifest(settings, refresh=True)
    print(f"wrote manifest: {settings.source_manifest_path}")
    print(f"entries: {len(entries)}")
    print(f"high-value entries: {sum(1 for entry in entries if entry.high_value)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

