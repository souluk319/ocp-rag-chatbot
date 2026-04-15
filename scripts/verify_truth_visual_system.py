from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    tsx = (root / "presentation-ui" / "src" / "pages" / "WorkspacePage.tsx").read_text(encoding="utf-8")
    css = (root / "presentation-ui" / "src" / "pages" / "WorkspacePage.css").read_text(encoding="utf-8")

    report = {
        "status": "ok",
        "tsx_has_truth_badge_block": "function TruthBadgeBlock" in tsx,
        "tsx_has_related_link_card": "function RelatedLinkCard" in tsx,
        "tsx_uses_related_link_card": "<RelatedLinkCard" in tsx,
        "tsx_uses_truth_badge_in_header": "badgeClassName=\"assistant-truth-chip\"" in tsx,
        "tsx_uses_truth_badge_in_session": "badgeClassName=\"session-truth-chip\"" in tsx,
        "css_has_related_link_card": ".related-link-card" in css,
        "css_has_related_link_badge": ".related-link-badge" in css,
        "css_has_shared_truth_visual_system": ".assistant-truth-chip,\n.session-truth-chip,\n.citation-tag-badge,\n.related-link-badge" in css,
    }
    if not all(report.values()):
        report["status"] = "failed"
        raise SystemExit(json.dumps(report, ensure_ascii=False))

    out = root / "reports" / "build_logs" / "truth_visual_system_report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
