from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ocp_rag_part1.settings import load_settings
from ocp_rag_part1.viewer import read_normalized_sections, write_viewer_docs


def main() -> int:
    settings = load_settings(ROOT)
    sections = read_normalized_sections(settings.normalized_docs_path)
    written = write_viewer_docs(sections, settings)
    print(f"viewer_doc_count={written}")
    print(f"viewer_docs_dir={settings.viewer_docs_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
