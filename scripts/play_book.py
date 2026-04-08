# play_book.cmd가 호출하는 얇은 CLI 진입점.
# 실제 제품 명령은 src/play_book_studio/cli.py가 처리하고, 이 파일은 연결만 맡는다.
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
