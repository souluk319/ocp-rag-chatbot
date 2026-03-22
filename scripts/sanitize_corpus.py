"""비공개 raw 코퍼스를 공개 가능한 정제본으로 변환."""
from __future__ import annotations

import os
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.chunker import DocumentParser
from src.config import DATA_PRIVATE_RAW_DIR, DATA_SANITIZED_DIR
from src.sanitizer import TextSanitizer


SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx", ".pptx"}


def destination_path(source_path: Path, source_root: Path, target_root: Path) -> Path:
    rel = source_path.relative_to(source_root)
    if source_path.suffix.lower() in {".md", ".txt"}:
        return target_root / rel
    return (target_root / rel).with_suffix(".md")


def sanitize_corpus() -> int:
    source_root = Path(DATA_PRIVATE_RAW_DIR)
    target_root = Path(DATA_SANITIZED_DIR)
    sanitizer = TextSanitizer()

    if not source_root.exists():
        print(f"소스 디렉토리가 없습니다: {source_root}")
        return 1

    target_root.mkdir(parents=True, exist_ok=True)
    counts: Counter[str] = Counter()
    written = 0

    for path in sorted(source_root.rglob("*")):
        if not path.is_file() or path.name.startswith(".") or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        text = DocumentParser.parse_file(str(path))
        result = sanitizer.sanitize(text)
        counts.update(result.counts)

        out_path = destination_path(path, source_root, target_root)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        header = f"<!-- source: {path.name} -->\n\n"
        out_path.write_text(header + result.text.strip() + "\n", encoding="utf-8")
        written += 1

    print("=" * 60)
    print("정제 코퍼스 생성 완료")
    print(f"  source: {source_root}")
    print(f"  target: {target_root}")
    print(f"  files:  {written}")
    for key, value in sorted(counts.items()):
        print(f"  {key}: {value}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(sanitize_corpus())
