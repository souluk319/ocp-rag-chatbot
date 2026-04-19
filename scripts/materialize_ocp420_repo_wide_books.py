from __future__ import annotations

import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
from play_book_studio.ingestion.official_rebuild import (
    normalize_inline_text_fragment,
    primary_heading_from_path,
    render_bound_markdown,
)
from play_book_studio.source_provenance import source_provenance_payload


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _manifest_path() -> Path:
    return ROOT / "manifests" / "ocp420_repo_wide_source_manifest.json"

def _gold_candidate_root() -> Path:
    return ROOT / "data" / "gold_candidate_books" / "repo_wide_official"


def _wiki_runtime_root() -> Path:
    return ROOT / "data" / "wiki_runtime_books" / "repo_wide_official"


def _gold_candidate_manifest_out() -> Path:
    return ROOT / "data" / "gold_candidate_books" / "repo_wide_official_manifest.json"


def _gold_candidate_catalog_out() -> Path:
    return ROOT / "data" / "gold_candidate_books" / "repo_wide_official_catalog.md"


def _wiki_runtime_manifest_out() -> Path:
    return ROOT / "data" / "wiki_runtime_books" / "repo_wide_official_manifest.json"


def _wiki_runtime_catalog_out() -> Path:
    return ROOT / "data" / "wiki_runtime_books" / "repo_wide_official_catalog.md"


def _report_out() -> Path:
    return ROOT / "reports" / "build_logs" / "ocp420_repo_wide_materialization_report.json"


def _wiki_asset_root() -> Path:
    return ROOT / "data" / "wiki_assets" / "repo_wide_official"


def _figure_asset_catalog_out() -> Path:
    return ROOT / "data" / "wiki_relations" / "repo_wide_official_figure_assets.json"


def _diagram_asset_catalog_out() -> Path:
    return ROOT / "data" / "wiki_relations" / "repo_wide_official_diagram_assets.json"


def _figure_viewer_path(slug: str, asset_url: str) -> str:
    asset_name = Path(urlparse(asset_url).path).name.strip()
    if not slug or not asset_name:
        return ""
    return f"/wiki/figures/{slug}/{asset_name}/index.html"


# local unmanaged source mirror; top-level git intentionally ignores tmp_source/
SOURCE_MIRROR_ROOT = ROOT / "tmp_source" / "openshift-docs-enterprise-4.20"
ASCIIDOC_IMAGE_RE = re.compile(r"^\s*image::(?P<target>[^\[]+)\[(?P<attrs>[^\]]*)\]", re.MULTILINE)
ASCIIDOC_INCLUDE_RE = re.compile(r"^\s*include::(?P<target>[^\[]+)\[[^\]]*\]", re.MULTILINE)
HTML_IMG_RE = re.compile(r"<img(?P<attrs>[^>]+)>", re.IGNORECASE)
HTML_ATTR_RE = re.compile(r'([a-zA-Z:_-]+)\s*=\s*"([^"]*)"')


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _clean_heading(text: str) -> str:
    return " ".join(str(text or "").split()).strip()


def _safe_asset_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()) or "asset"


def _resolve_include_path(source_file: Path, include_target: str) -> Path | None:
    normalized = include_target.strip()
    if not normalized or "{" in normalized or "}" in normalized:
        return None
    candidates = [(source_file.parent / normalized).resolve()]
    candidates.append((SOURCE_MIRROR_ROOT / normalized).resolve())
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def _resolve_image_asset(source_file: Path, asset_target: str) -> Path | None:
    normalized = asset_target.strip()
    if not normalized or "{" in normalized or "}" in normalized:
        return None
    candidates = [
        (source_file.parent / normalized).resolve(),
        (SOURCE_MIRROR_ROOT / normalized).resolve(),
        (SOURCE_MIRROR_ROOT / "images" / normalized).resolve(),
        (SOURCE_MIRROR_ROOT / "_images" / normalized).resolve(),
    ]
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def _figure_caption(attrs: str, fallback_name: str) -> str:
    tokens = [token.strip() for token in (attrs or "").split(",") if token.strip()]
    if tokens:
        return normalize_inline_text_fragment(tokens[0]).strip() or fallback_name
    return normalize_inline_text_fragment(fallback_name).strip() or fallback_name


DIAGRAM_KEYWORDS = (
    "diagram",
    "architecture",
    "architectural",
    "topology",
    "workflow",
    "flow",
    "구성도",
    "아키텍처",
    "토폴로지",
    "워크플로",
    "흐름",
    "개요",
    "구성",
    "다이어그램",
)


def _classify_figure_asset(*, caption: str, alt: str, source_asset_ref: str, section_hint: str) -> tuple[str, str]:
    normalized_asset = (source_asset_ref or "").strip().lower()
    if normalized_asset.endswith(".svg"):
        return "diagram", "vector_svg"
    text = " ".join(
        part.strip().lower()
        for part in (caption, alt, section_hint, Path(normalized_asset).stem.replace("_", " "))
        if part and str(part).strip()
    )
    if any(token in text for token in DIAGRAM_KEYWORDS):
        return "diagram", "semantic_diagram"
    return "figure", "image_figure"


def _render_figure_marker(figure: dict[str, str], index: int) -> list[str]:
    caption = str(figure.get("caption") or f"Figure {index}").strip()
    asset_url = str(figure.get("asset_url") or "").strip()
    source_file = str(figure.get("source_file") or "").strip()
    source_asset_ref = str(figure.get("source_asset_ref") or "").strip()
    alt = str(figure.get("alt") or caption).strip()
    asset_kind = str(figure.get("asset_kind") or "figure").strip()
    diagram_type = str(figure.get("diagram_type") or "").strip()
    if not asset_url:
        return []
    marker = (
        '[FIGURE src="{src}" alt="{alt}" kind="{kind}" diagram_type="{diagram_type}"]\n{caption}\n[/FIGURE]'
    ).format(
        src=asset_url.replace('"', "&quot;"),
        alt=alt.replace('"', "&quot;"),
        kind=asset_kind.replace('"', "&quot;"),
        diagram_type=diagram_type.replace('"', "&quot;"),
        caption=caption,
    )
    source_line = f"_Source: `{Path(source_file).name}` · asset `{source_asset_ref}`_"
    return [marker, "", source_line, ""]


def _extract_asciidoc_figures_from_file(path: Path, seen: set[Path], *, section_hint: str) -> list[dict[str, str]]:
    if path in seen or not path.exists() or not path.is_file():
        return []
    seen.add(path)
    text = path.read_text(encoding="utf-8", errors="ignore")
    figures: list[dict[str, str]] = []
    for match in ASCIIDOC_IMAGE_RE.finditer(text):
        asset_target = str(match.group("target") or "").strip()
        asset_path = _resolve_image_asset(path, asset_target)
        if asset_path is None:
            continue
        caption = _figure_caption(str(match.group("attrs") or ""), Path(asset_target).stem.replace("_", " "))
        figures.append(
            {
                "source_file": str(path.resolve()),
                "source_asset_ref": asset_target,
                "asset_path": str(asset_path.resolve()),
                "caption": caption,
                "alt": caption,
                "section_hint": section_hint,
            }
        )
    for match in ASCIIDOC_INCLUDE_RE.finditer(text):
        include_target = str(match.group("target") or "").strip()
        include_path = _resolve_include_path(path, include_target)
        if include_path is None:
            continue
        figures.extend(_extract_asciidoc_figures_from_file(include_path, seen, section_hint=section_hint))
    return figures


def _materialize_figures(
    *,
    slug: str,
    source_relative_paths: list[str],
    asset_group: str,
) -> list[dict[str, str]]:
    extracted: list[dict[str, str]] = []
    for source_relative_path in source_relative_paths:
        source_path = (SOURCE_MIRROR_ROOT / source_relative_path).resolve()
        section_hint = primary_heading_from_path(source_path)
        extracted.extend(_extract_asciidoc_figures_from_file(source_path, set(), section_hint=section_hint))
    if not extracted:
        return []
    deduped: list[dict[str, str]] = []
    seen_assets: set[tuple[str, str]] = set()
    for figure in extracted:
        dedupe_key = (
            str(figure.get("source_asset_ref") or "").strip().lower(),
            re.sub(r"\s+", " ", str(figure.get("caption") or "")).strip().lower(),
        )
        if dedupe_key in seen_assets:
            continue
        seen_assets.add(dedupe_key)
        deduped.append(figure)
    slug_asset_root = _wiki_asset_root() / slug
    slug_asset_root.mkdir(parents=True, exist_ok=True)
    rendered: list[dict[str, str]] = []
    used_names: set[str] = set()
    for index, figure in enumerate(deduped, start=1):
        asset_path = Path(figure["asset_path"])
        base_name = _safe_asset_name(asset_path.name)
        target_name = base_name
        if target_name in used_names:
            target_name = f"{asset_path.stem}-{index}{asset_path.suffix}"
        used_names.add(target_name)
        target_path = slug_asset_root / target_name
        shutil.copy2(asset_path, target_path)
        rendered.append(
            {
                "caption": figure["caption"],
                "alt": figure["alt"],
                "source_file": figure["source_file"],
                "source_asset_ref": figure["source_asset_ref"],
                "section_hint": str(figure.get("section_hint") or "").strip(),
                "asset_path": str(target_path.resolve()),
                "asset_url": f"/playbooks/wiki-assets/{asset_group}/{slug}/{target_name}",
            }
        )
    return rendered


def _append_figure_gallery(markdown_text: str, *, figures: list[dict[str, str]]) -> str:
    if not figures:
        return markdown_text
    parts = [markdown_text.rstrip(), "", "## Figures", ""]
    for index, figure in enumerate(figures, start=1):
        caption = str(figure.get("caption") or f"Figure {index}").strip()
        if not str(figure.get("asset_url") or "").strip():
            continue
        parts.extend(
            [
                f"### Figure {index}. {caption}",
                "",
                *_render_figure_marker(figure, index),
            ]
        )
    return "\n".join(parts).strip() + "\n"


def _normalize_heading_key(text: str) -> str:
    normalized = re.sub(r"[^\w\s가-힣-]", " ", str(text or ""), flags=re.UNICODE)
    normalized = re.sub(r"\s+", " ", normalized).strip().lower()
    return normalized


def _inline_figure_markdown(figure: dict[str, str], index: int) -> list[str]:
    return _render_figure_marker(figure, index)


def _place_figures_inline(
    markdown_text: str,
    *,
    figures: list[dict[str, str]],
    section_hints: dict[str, str],
    drop_unmatched: bool = False,
) -> tuple[str, dict[str, int], list[dict[str, str]]]:
    if not figures:
        return markdown_text, {"figure_count": 0, "inline_placed": 0, "gallery_fallback": 0, "dropped_unmatched": 0}, []
    lines = markdown_text.splitlines()
    heading_positions: dict[str, int] = {}
    heading_line_re = re.compile(r"^(#+)\s+(.*)$")
    for index, line in enumerate(lines):
        match = heading_line_re.match(line.strip())
        if not match:
            continue
        heading_key = _normalize_heading_key(match.group(2))
        if heading_key and heading_key not in heading_positions:
            heading_positions[heading_key] = index

    placed_indices: set[int] = set()
    insertions: dict[int, list[str]] = {}
    for idx, figure in enumerate(figures, start=1):
        asset_basename = Path(str(figure.get("source_asset_ref") or "")).name
        hint = str(figure.get("section_hint") or section_hints.get(asset_basename, "")).strip()
        hint_key = _normalize_heading_key(hint)
        if not hint_key:
            continue
        target_index = None
        for heading_key, position in heading_positions.items():
            if hint_key == heading_key or hint_key in heading_key or heading_key in hint_key:
                target_index = position
                break
        if target_index is None:
            continue
        placed_indices.add(idx - 1)
        insertions.setdefault(target_index, []).extend([""] + _inline_figure_markdown(figure, idx))

    output: list[str] = []
    for index, line in enumerate(lines):
        output.append(line)
        if index in insertions:
            output.extend(insertions[index])

    remaining = [figure for idx, figure in enumerate(figures) if idx not in placed_indices]
    dropped_unmatched = 0
    if drop_unmatched and remaining:
        dropped_unmatched = len(remaining)
        remaining = []
    visible_figures = [figure for idx, figure in enumerate(figures) if idx in placed_indices] + remaining
    rendered_markdown = _append_figure_gallery("\n".join(output).rstrip() + "\n", figures=remaining)
    return rendered_markdown, {
        "figure_count": len(figures),
        "inline_placed": len(placed_indices),
        "gallery_fallback": len(remaining),
        "dropped_unmatched": dropped_unmatched,
    }, visible_figures


def _catalog_markdown(title: str, generated_at: str, entries: list[dict[str, str]], kind_key: str) -> str:
    lines = [
        f"# {title}",
        "",
        "## 현재 판단",
        "",
        "이 카탈로그는 OCP 4.20 repo-wide official rebuild 기준으로 물질화된 md 북만 모아둔 것이다.",
        "",
        f"- generated_at_utc: `{generated_at}`",
        "",
        "## Entries",
        "",
    ]
    for item in entries:
        lines.extend(
            [
                f"### `{item['slug']}`",
                "",
                f"- title: `{item['title']}`",
                f"- {kind_key}: [{Path(item[kind_key]).name}]({item[kind_key]})",
                f"- source_manifest_slug: `{item['slug']}`",
                f"- source_kind: `{item.get('source_kind', 'runtime_from_candidate')}`",
                f"- promotion_strategy: `{item['promotion_strategy']}`",
                "",
            ]
        )
    return "\n".join(lines).strip() + "\n"


def _load_relation_entities() -> dict[str, list[dict[str, str]]]:
    path = ROOT / "data" / "wiki_relations" / "candidate_relations.json"
    if not path.exists():
        return {}
    payload = _load_json(path)
    result: dict[str, list[dict[str, str]]] = {}
    for slug, relation in payload.items():
        if not isinstance(slug, str) or not isinstance(relation, dict):
            continue
        entities = [item for item in relation.get("entities", []) if isinstance(item, dict)]
        result[slug] = entities
    return result


def main() -> int:
    manifest = _load_json(_manifest_path())
    manifest_entries = manifest.get("entries") if isinstance(manifest.get("entries"), list) else []
    blocked_manifest_entries = [
        {
            "book_slug": str(entry.get("book_slug") or "").strip(),
            "rebuild_admission": str(entry.get("rebuild_admission") or "").strip(),
        }
        for entry in manifest_entries
        if isinstance(entry, dict) and str(entry.get("rebuild_admission") or "").strip() != "repo_source_ready"
    ]
    if str(manifest.get("status") or "").strip() == "blocked" or blocked_manifest_entries:
        blocked_payload = {
            "status": "blocked",
            "reason": "repo-wide official manifest still contains entries without repo/AsciiDoc source binding",
            "blocked_entries": blocked_manifest_entries or list(manifest.get("blocked_entries") or []),
        }
        _report_out().parent.mkdir(parents=True, exist_ok=True)
        _report_out().write_text(
            json.dumps(blocked_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(json.dumps(blocked_payload, ensure_ascii=False, indent=2))
        return 2

    _gold_candidate_root().mkdir(parents=True, exist_ok=True)
    _wiki_runtime_root().mkdir(parents=True, exist_ok=True)
    _wiki_asset_root().mkdir(parents=True, exist_ok=True)
    _report_out().parent.mkdir(parents=True, exist_ok=True)

    candidate_entries: list[dict[str, str]] = []
    runtime_entries: list[dict[str, str]] = []
    generation_mode_counter = {"repo_source_binding": 0}
    figure_stats: dict[str, int] = {}
    diagram_stats: dict[str, int] = {}
    inline_placed_stats: dict[str, int] = {}
    gallery_fallback_stats: dict[str, int] = {}
    dropped_unmatched_stats: dict[str, int] = {}
    figure_assets_by_slug: dict[str, list[dict[str, Any]]] = {}
    diagram_assets_by_slug: dict[str, list[dict[str, Any]]] = {}
    relation_entities_by_slug = _load_relation_entities()
    generated_at = _utc_now()

    for entry in manifest_entries:
        if not isinstance(entry, dict):
            continue
        slug = str(entry.get("book_slug") or "").strip()
        title = str(entry.get("title") or slug).strip() or slug
        if not slug:
            continue

        target_paths = entry.get("rebuild_target_paths") if isinstance(entry.get("rebuild_target_paths"), dict) else {}
        candidate_path = ROOT / str(target_paths.get("gold_candidate_md") or f"data/gold_candidate_books/repo_wide_official/{slug}.md")
        runtime_path = ROOT / str(target_paths.get("wiki_runtime_md") or f"data/wiki_runtime_books/repo_wide_official/{slug}.md")
        candidate_path.parent.mkdir(parents=True, exist_ok=True)
        runtime_path.parent.mkdir(parents=True, exist_ok=True)

        source_kind = "official_repo_asciidoc_binding"
        promotion_strategy = "repo_wide_official_source_repo_binding"
        source_binding_kind = str(entry.get("source_binding_kind") or "file").strip() or "file"
        source_relative_paths = [
            str(item).strip()
            for item in (entry.get("source_relative_paths") or [])
            if str(item).strip()
        ]
        if not source_relative_paths:
            source_relative_path = str(entry.get("source_relative_path") or "").strip()
            if source_relative_path.endswith(".adoc"):
                source_relative_paths = [source_relative_path]
        source_paths = [(SOURCE_MIRROR_ROOT / relative_path).resolve() for relative_path in source_relative_paths]
        markdown_text = render_bound_markdown(
            title=title,
            source_paths=source_paths,
            binding_kind=source_binding_kind,
        )
        generation_mode_counter["repo_source_binding"] += 1

        figures = _materialize_figures(
            slug=slug,
            source_relative_paths=source_relative_paths,
            asset_group="repo_wide_official",
        )
        for figure in figures:
            asset_kind, diagram_type = _classify_figure_asset(
                caption=str(figure.get("caption") or ""),
                alt=str(figure.get("alt") or ""),
                source_asset_ref=str(figure.get("source_asset_ref") or ""),
                section_hint=str(figure.get("section_hint") or ""),
            )
            figure["asset_kind"] = asset_kind
            figure["diagram_type"] = diagram_type
        markdown_text, placement_stats, visible_figures = _place_figures_inline(
            markdown_text,
            figures=figures,
            section_hints={},
            drop_unmatched=False,
        )
        figure_stats[slug] = int(placement_stats.get("figure_count", 0))
        diagram_stats[slug] = sum(1 for figure in figures if str(figure.get("asset_kind") or "") == "diagram")
        inline_placed_stats[slug] = int(placement_stats.get("inline_placed", 0))
        gallery_fallback_stats[slug] = int(placement_stats.get("gallery_fallback", 0))
        dropped_unmatched_stats[slug] = int(placement_stats.get("dropped_unmatched", 0))
        figure_assets_by_slug[slug] = [
            {
                "caption": str(figure.get("caption") or "").strip(),
                "alt": str(figure.get("alt") or "").strip(),
                "asset_kind": str(figure.get("asset_kind") or "figure").strip(),
                "diagram_type": str(figure.get("diagram_type") or "").strip(),
                "asset_url": str(figure.get("asset_url") or "").strip(),
                "viewer_path": _figure_viewer_path(slug, str(figure.get("asset_url") or "").strip()),
                "source_file": str(figure.get("source_file") or "").strip(),
                "source_asset_ref": str(figure.get("source_asset_ref") or "").strip(),
                "section_hint": str(figure.get("section_hint") or "").strip(),
                "related_entities": relation_entities_by_slug.get(slug, []),
            }
            for figure in visible_figures
            if str(figure.get("asset_url") or "").strip()
        ]
        diagram_assets_by_slug[slug] = [
            asset
            for asset in figure_assets_by_slug[slug]
            if str(asset.get("asset_kind") or "") == "diagram"
        ]

        candidate_path.write_text(markdown_text, encoding="utf-8")
        runtime_path.write_text(markdown_text, encoding="utf-8")

        candidate_entries.append(
            {
                "slug": slug,
                "title": title,
                "source_kind": source_kind,
                "source_binding_kind": source_binding_kind,
                "source_lane": str(entry.get("source_lane") or ""),
                "source_ref": str(source_provenance_payload(entry).get("source_ref") or ""),
                "source_fingerprint": str(source_provenance_payload(entry).get("source_fingerprint") or ""),
                "source_repo": str(entry.get("source_repo") or ""),
                "source_branch": str(entry.get("source_branch") or ""),
                "source_relative_path": str(entry.get("source_relative_path") or ""),
                "source_relative_paths": list(source_provenance_payload(entry).get("source_relative_paths") or []),
                "fallback_source_url": str(entry.get("fallback_source_url") or ""),
                "fallback_viewer_path": str(entry.get("fallback_viewer_path") or ""),
                "source_manifest_path": str(_manifest_path().resolve()),
                "promoted_path": str(candidate_path.resolve()),
                "source_trial_path": str(candidate_path.resolve()),
                "promotion_strategy": promotion_strategy,
                "parser_route": "source_first_repo_binding",
                "parser_backend": "render_bound_markdown",
                "updated_at": generated_at,
            }
        )
        runtime_entries.append(
            {
                "slug": slug,
                "title": title,
                "source_lane": str(entry.get("source_lane") or ""),
                "source_ref": str(source_provenance_payload(entry).get("source_ref") or ""),
                "source_fingerprint": str(source_provenance_payload(entry).get("source_fingerprint") or ""),
                "source_repo": str(entry.get("source_repo") or ""),
                "source_branch": str(entry.get("source_branch") or ""),
                "source_binding_kind": source_binding_kind,
                "source_relative_path": str(entry.get("source_relative_path") or ""),
                "source_relative_paths": list(source_provenance_payload(entry).get("source_relative_paths") or []),
                "fallback_source_url": str(entry.get("fallback_source_url") or ""),
                "fallback_viewer_path": str(entry.get("fallback_viewer_path") or ""),
                "source_candidate_path": str(candidate_path.resolve()),
                "runtime_path": str(runtime_path.resolve()),
                "promotion_strategy": promotion_strategy,
                "source_manifest_path": str(_manifest_path().resolve()),
                "parser_route": "source_first_repo_binding",
                "parser_backend": "render_bound_markdown",
                "updated_at": generated_at,
            }
        )

        processed_count = len(runtime_entries)
        if processed_count % 100 == 0:
            print(
                json.dumps(
                    {
                        "stage": "materializing",
                        "processed_count": processed_count,
                        "entry_count": len(manifest_entries),
                        "last_slug": slug,
                    },
                    ensure_ascii=False,
                )
            )

    candidate_manifest = {
        "generated_at_utc": generated_at,
        "candidate_count": len(candidate_entries),
        "promotion_group": "repo_wide_official_gold_candidates",
        "entries": candidate_entries,
    }
    runtime_manifest = {
        "generated_at_utc": generated_at,
        "runtime_count": len(runtime_entries),
        "promotion_group": "repo_wide_official_wiki_runtime",
        "source_strategy": str(manifest.get("source_strategy") or ""),
        "source_manifest_path": str(_manifest_path().resolve()),
        "entries": runtime_entries,
    }

    _gold_candidate_manifest_out().write_text(json.dumps(candidate_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    _wiki_runtime_manifest_out().write_text(json.dumps(runtime_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    _gold_candidate_catalog_out().write_text(
        _catalog_markdown("OCP 4.20 Repo-Wide Official Gold Candidate Catalog", generated_at, candidate_entries, "promoted_path"),
        encoding="utf-8",
    )
    _wiki_runtime_catalog_out().write_text(
        _catalog_markdown("OCP 4.20 Repo-Wide Official Wiki Runtime Catalog", generated_at, runtime_entries, "runtime_path"),
        encoding="utf-8",
    )
    _figure_asset_catalog_out().write_text(
        json.dumps(
            {
                "generated_at_utc": generated_at,
                "book_count": len(figure_assets_by_slug),
                "entries": figure_assets_by_slug,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    _diagram_asset_catalog_out().write_text(
        json.dumps(
            {
                "generated_at_utc": generated_at,
                "book_count": sum(1 for assets in diagram_assets_by_slug.values() if assets),
                "diagram_count": sum(len(assets) for assets in diagram_assets_by_slug.values()),
                "entries": {slug: assets for slug, assets in diagram_assets_by_slug.items() if assets},
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    _report_out().write_text(
        json.dumps(
            {
                "status": "ok",
                "generated_at_utc": generated_at,
                "manifest_path": str(_manifest_path().resolve()),
                "candidate_manifest_path": str(_gold_candidate_manifest_out().resolve()),
                "runtime_manifest_path": str(_wiki_runtime_manifest_out().resolve()),
                "candidate_count": len(candidate_entries),
                "runtime_count": len(runtime_entries),
                "generation_modes": generation_mode_counter,
                "figure_counts_by_slug": figure_stats,
                "diagram_counts_by_slug": diagram_stats,
                "inline_placed_figure_counts_by_slug": inline_placed_stats,
                "gallery_fallback_figure_counts_by_slug": gallery_fallback_stats,
                "dropped_unmatched_figure_counts_by_slug": dropped_unmatched_stats,
                "figure_asset_root": str(_wiki_asset_root().resolve()),
                "figure_asset_catalog_path": str(_figure_asset_catalog_out().resolve()),
                "diagram_asset_catalog_path": str(_diagram_asset_catalog_out().resolve()),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": "ok",
                "candidate_count": len(candidate_entries),
                "runtime_count": len(runtime_entries),
                "generation_modes": generation_mode_counter,
                "figure_enabled_slugs": sum(1 for count in figure_stats.values() if count > 0),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    from play_book_studio.execution_guard import run_guarded_script

    raise SystemExit(
        run_guarded_script(
            main,
            __file__,
            launcher_hint="scripts/codex_python.ps1",
        )
    )
