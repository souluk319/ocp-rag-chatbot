from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.config.settings import load_settings
from play_book_studio.ingestion.synthesis_lane import write_synthesis_lane_outputs
from play_book_studio.ingestion.topic_playbooks import materialize_topic_playbooks


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Promote bronze bundle readiness into translation/manual-review working sets.",
    )
    return parser


def main() -> int:
    build_parser().parse_args()
    settings = load_settings(ROOT)
    materialize_topic_playbooks(settings)
    report = write_synthesis_lane_outputs(settings)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    from play_book_studio.execution_guard import run_guarded_script

    raise SystemExit(run_guarded_script(main, __file__, launcher_hint="scripts/codex_python.ps1"))
