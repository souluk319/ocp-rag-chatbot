from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.runtime_config import load_runtime_config


def main() -> int:
    config = load_runtime_config()
    summary = config.to_health_dict()
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if summary["missing_required_keys"]:
        print("Runtime contract is incomplete.", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
