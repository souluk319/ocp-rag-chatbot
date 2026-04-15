from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    workspace_page = (root / "presentation-ui" / "src" / "pages" / "WorkspacePage.tsx").read_text(encoding="utf-8")
    workspace_css = (root / "presentation-ui" / "src" / "pages" / "WorkspacePage.css").read_text(encoding="utf-8")

    report = {
        "status": "ok",
        "tsx_has_citation_surface_copy": "function citationSurfaceCopy" in workspace_page,
        "tsx_has_citation_tag_component": "function CitationTag" in workspace_page,
        "tsx_uses_citation_tag_component": "<CitationTag" in workspace_page,
        "css_has_citation_badge": ".citation-tag-badge" in workspace_css,
        "css_has_citation_title": ".citation-tag-title" in workspace_css,
        "css_has_citation_meta": ".citation-tag-meta" in workspace_css,
        "css_has_citation_topline": ".citation-tag-topline" in workspace_css,
    }
    if not all(report.values()):
        report["status"] = "failed"
        raise SystemExit(json.dumps(report, ensure_ascii=False))

    out = root / "reports" / "build_logs" / "mixed_runtime_visual_hierarchy_report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
