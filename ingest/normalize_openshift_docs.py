from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import subprocess
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]


DEFAULT_INCLUDE_DIRS = [
    "installing",
    "post_installation_configuration",
    "updating",
    "disconnected",
    "support",
]

DEFAULT_EXCLUDE_PREFIXES = (
    "osd_",
    "rosa_",
    "microshift_",
    "cloud_experts_",
)

DEFAULT_EXCLUDE_PATH_FRAGMENTS = (
    "/rosa-",
    "/rosa_",
    "-rosa-",
    "_rosa_",
    "/osd-",
    "/osd_",
    "-osd-",
    "_osd_",
    "/microshift-",
    "/microshift_",
    "-microshift-",
    "_microshift_",
    "/support/remote_health_monitoring/",
    "/support/troubleshooting/rosa-",
    "/support/troubleshooting/troubleshooting-osd-",
    "/support/troubleshooting/sd-",
)

DEFAULT_EXCLUDE_DIRS = {
    "modules",
    "snippets",
    "_topic_maps",
    "_images",
    "_templates",
    "_attributes",
    "_stylesheets",
    "_javascripts",
    "_converters",
    "_gemfiles",
    "ocm",
    "hosted_control_planes",
    "lightspeed",
    "migration_toolkit_for_containers",
    "contributing_to_docs",
}

HEADING_RE = re.compile(r"^(=+)\s+(.*)$")
ID_RE = re.compile(r'^\[id="([^"]+)"\]\s*$')
ATTR_RE = re.compile(r"^:([A-Za-z0-9_.!-]+):\s*(.*)$")
IFDEF_RE = re.compile(r"^ifdef::([^\[]+)\[\]\s*$")
IFNDEF_RE = re.compile(r"^ifndef::([^\[]+)\[\]\s*$")
ENDIF_RE = re.compile(r"^endif::(?:[^\[]*)\[\]\s*$")
IFEVAL_CONTEXT_RE = re.compile(r'^ifeval::\["\{context\}"\s*==\s*"([^"]+)"\]\s*$')
INCLUDE_RE = re.compile(r"^include::([^\[]+)\[([^\]]*)\]\s*$")
LEVEL_OFFSET_RE = re.compile(r"leveloffset=([+-]?\d+)")
ADMONITION_RE = re.compile(r"^\[(NOTE|IMPORTANT|WARNING|TIP|CAUTION)\]\s*$")
SOURCE_BLOCK_RE = re.compile(r"^\[source(?:,([^\]]+))?\]\s*$")


@dataclass
class ParserState:
    context_value: str = ""
    attrs: set[str] = field(default_factory=set)
    attr_values: dict[str, str] = field(default_factory=dict)


@dataclass
class RenderSection:
    section_id: str
    title: str
    anchor_id: str
    level: int
    heading_hierarchy: list[str]
    section_index: int
    body_lines: list[str] = field(default_factory=list)


@dataclass
class NormalizedDocument:
    document_id: str
    title: str
    source_id: str
    source_type: str
    source_mirror_id: str
    source_profile_id: str
    source_url: str
    source_git_ref: str
    source_git_commit: str
    local_path: str
    normalized_path: str
    html_path: str
    viewer_url: str
    product: str
    version: str
    target_minor: str | None
    category: str
    language: str
    trust_level: str
    collected_at: str
    checksum: str
    top_level_dir: str
    section_count: int
    sections: list[dict[str, object]]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize selected openshift-docs AsciiDoc content into text plus HTML citation views."
    )
    parser.add_argument(
        "--profile-catalog",
        type=Path,
        default=Path("./configs/source-profiles.yaml"),
        help="Path to the source profile catalog.",
    )
    parser.add_argument(
        "--active-profile-config",
        type=Path,
        default=Path("./configs/active-source-profile.yaml"),
        help="Path to the active source profile selection file.",
    )
    parser.add_argument(
        "--profile-id",
        default="",
        help="Explicit source profile id. Overrides active-source-profile.yaml when set.",
    )
    parser.add_argument(
        "--target-minor",
        default="",
        help="Target OCP minor such as 4.17. Required for target-minor profiles.",
    )
    parser.add_argument(
        "--source-root",
        type=Path,
        default=Path("../openshift-docs"),
        help="Path to the openshift-docs checkout",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("./data/normalized/openshift-docs-p0"),
        help="Directory where normalized text files will be written",
    )
    parser.add_argument(
        "--html-dir",
        type=Path,
        default=Path("./data/views/openshift-docs-p0"),
        help="Directory where HTML citation views will be written",
    )
    parser.add_argument(
        "--manifest-out",
        type=Path,
        default=Path("./data/manifests/generated/openshift-docs-p0.json"),
        help="Path to the generated manifest JSON file",
    )
    parser.add_argument(
        "--include-dir",
        action="append",
        dest="include_dirs",
        help="Top-level openshift-docs directory to include. Repeat to add more.",
    )
    parser.add_argument(
        "--source-id",
        default="openshift-docs-p0",
        help="Source identifier written to the manifest",
    )
    parser.add_argument(
        "--exclude-fragment",
        action="append",
        dest="exclude_fragments",
        help="Case-insensitive path fragment to exclude. Repeat to add more.",
    )
    parser.add_argument(
        "--version-label",
        default="4.x",
        help="Version label stored in the manifest",
    )
    parser.add_argument(
        "--allow-ref-mismatch",
        action="store_true",
        help="Allow normalization even when the checked-out git ref does not match the resolved profile ref.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List selected files without writing output",
    )
    parser.add_argument(
        "--show-documents",
        action="store_true",
        help="When used with --dry-run, print the full document list instead of a summary.",
    )
    return parser.parse_args()


def should_skip_top_level(name: str, exclude_dirs: set[str], exclude_prefixes: tuple[str, ...]) -> bool:
    if name in exclude_dirs:
        return True
    return any(name.startswith(prefix) for prefix in exclude_prefixes)


def normalize_match_path(relative_path: Path) -> str:
    return f"/{relative_path.as_posix().lower()}"


def skip_reason_for_path(
    relative_path: Path,
    exclude_fragments: list[str],
    exclude_dirs: set[str],
    exclude_prefixes: tuple[str, ...],
) -> str | None:
    top_level = relative_path.parts[0]
    if should_skip_top_level(top_level, exclude_dirs, exclude_prefixes):
        return f"top_level:{top_level}"

    normalized_path = normalize_match_path(relative_path)
    for fragment in exclude_fragments:
        if fragment.lower() in normalized_path:
            return f"path_fragment:{fragment}"
    return None


def collect_source_files(source_root: Path, include_dirs: list[str]) -> list[Path]:
    files: list[Path] = []
    for dirname in include_dirs:
        top_dir = source_root / dirname
        if not top_dir.exists():
            print(f"[warn] missing include dir: {top_dir}")
            continue
        files.extend(sorted(top_dir.rglob("*.adoc")))
    return files


def build_source_url(relative_path: Path, ref: str, source_url_base: str) -> str:
    return f"{source_url_base.rstrip('/')}/blob/{ref}/{relative_path.as_posix()}"


def build_viewer_url(source_id: str, relative_path: Path) -> str:
    return f"/viewer/{source_id}/{relative_path.with_suffix('.html').as_posix()}"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def stable_document_id(relative_path: Path) -> str:
    return hashlib.sha1(relative_path.as_posix().encode("utf-8")).hexdigest()


def stable_section_id(document_id: str, anchor_id: str, section_index: int) -> str:
    payload = f"{document_id}:{anchor_id}:{section_index}"
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()


def load_yaml_file(path: Path) -> dict:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {}
    return payload or {}


def format_profile_value(value, target_minor: str | None):
    if isinstance(value, str) and target_minor:
        return value.format(target_minor=target_minor)
    if isinstance(value, list):
        return [format_profile_value(item, target_minor) for item in value]
    if isinstance(value, dict):
        return {key: format_profile_value(item, target_minor) for key, item in value.items()}
    return value


def resolve_path_from_config(raw_path: str | None, *, base_dir: Path, fallback: Path) -> Path:
    if not raw_path:
        return fallback
    candidate = Path(raw_path)
    if candidate.is_absolute():
        return candidate
    return (base_dir / candidate).resolve()


def resolve_source_profile(args: argparse.Namespace) -> dict[str, object]:
    active_profile_id = args.profile_id.strip()
    target_minor = args.target_minor.strip() or None
    active_config_path = args.active_profile_config.resolve()
    profile_catalog_path = args.profile_catalog.resolve()
    active_config = load_yaml_file(active_config_path)
    catalog = load_yaml_file(profile_catalog_path)

    if not active_profile_id:
        active_profile_id = str(active_config.get("active_profile_id", "")).strip()
    if not target_minor:
        raw_target_minor = active_config.get("target_minor")
        if raw_target_minor not in (None, ""):
            target_minor = str(raw_target_minor).strip()

    if not active_profile_id:
        return {
            "profile_id": "",
            "purpose": "manual",
            "corpus_scope": "",
            "mirror_id": "",
            "source_root": args.source_root.resolve(),
            "source_id": args.source_id,
            "version_label": args.version_label,
            "include_dirs": args.include_dirs or DEFAULT_INCLUDE_DIRS,
            "exclude_fragments": args.exclude_fragments or list(DEFAULT_EXCLUDE_PATH_FRAGMENTS),
            "product": "ocp",
            "language": "en",
            "trust_level": "official",
            "source_type": "git_mirror",
            "source_url_base": "https://github.com/openshift/openshift-docs",
            "declared_git_ref": "main",
            "target_minor": None,
            "catalog_path": str(profile_catalog_path),
            "active_config_path": str(active_config_path) if active_config_path.exists() else "",
        }

    mirrors = {
        str(item.get("id", "")).strip(): item
        for item in catalog.get("mirrors", [])
        if str(item.get("id", "")).strip()
    }
    profiles = {
        str(item.get("id", "")).strip(): item
        for item in catalog.get("profiles", [])
        if str(item.get("id", "")).strip()
    }
    if active_profile_id not in profiles:
        raise SystemExit(f"Unknown source profile id: {active_profile_id}")

    profile = dict(profiles[active_profile_id])
    if profile.get("target_minor_required") and not target_minor:
        raise SystemExit(f"Source profile `{active_profile_id}` requires --target-minor or active target_minor.")
    profile = format_profile_value(profile, target_minor)
    mirror_id = str(profile.get("mirror_id", "")).strip()
    if mirror_id not in mirrors:
        raise SystemExit(f"Unknown mirror id `{mirror_id}` for source profile `{active_profile_id}`")
    mirror = format_profile_value(dict(mirrors[mirror_id]), target_minor)

    source_id = str(profile.get("source_id") or profile.get("source_id_template") or args.source_id).strip()
    version_label = str(profile.get("version_label") or profile.get("version_label_template") or args.version_label).strip()
    declared_git_ref = str(profile.get("git_ref") or profile.get("git_ref_template") or mirror.get("default_ref", "main")).strip()
    source_root = resolve_path_from_config(
        str(profile.get("local_path") or mirror.get("local_path") or ""),
        base_dir=REPO_ROOT,
        fallback=args.source_root.resolve(),
    )

    return {
        "profile_id": active_profile_id,
        "purpose": str(profile.get("purpose", "")).strip(),
        "corpus_scope": str(profile.get("corpus_scope", "")).strip(),
        "mirror_id": mirror_id,
        "source_root": source_root,
        "source_id": source_id,
        "version_label": version_label,
        "include_dirs": list(profile.get("include_dirs", args.include_dirs or DEFAULT_INCLUDE_DIRS)),
        "exclude_dirs": set(profile.get("exclude_dirs", list(DEFAULT_EXCLUDE_DIRS))),
        "exclude_prefixes": tuple(profile.get("exclude_prefixes", list(DEFAULT_EXCLUDE_PREFIXES))),
        "exclude_fragments": list(profile.get("exclude_path_fragments", args.exclude_fragments or list(DEFAULT_EXCLUDE_PATH_FRAGMENTS))),
        "product": str(mirror.get("product", "ocp")).strip(),
        "language": str(mirror.get("language", "en")).strip(),
        "trust_level": str(mirror.get("trust_level", "official")).strip(),
        "source_type": str(mirror.get("type", "git_mirror")).strip(),
        "source_url_base": str(mirror.get("source_url", "https://github.com/openshift/openshift-docs")).strip(),
        "declared_git_ref": declared_git_ref,
        "target_minor": target_minor,
        "catalog_path": str(profile_catalog_path),
        "active_config_path": str(active_config_path) if active_config_path.exists() else "",
    }


def git_output(repo_path: Path, *git_args: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_path), *git_args],
            capture_output=True,
            text=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""
    return result.stdout.strip()


def detect_source_lineage(source_root: Path, declared_git_ref: str) -> dict[str, object]:
    remote_url = git_output(source_root, "config", "--get", "remote.origin.url")
    detected_git_ref = git_output(source_root, "rev-parse", "--abbrev-ref", "HEAD")
    detected_git_commit = git_output(source_root, "rev-parse", "HEAD")
    dirty_state = git_output(source_root, "status", "--short")
    git_ref_matches_profile = (
        not declared_git_ref
        or detected_git_ref == declared_git_ref
        or detected_git_commit == declared_git_ref
    )
    return {
        "remote_url": remote_url,
        "declared_git_ref": declared_git_ref,
        "detected_git_ref": detected_git_ref,
        "detected_git_commit": detected_git_commit,
        "git_ref_matches_profile": git_ref_matches_profile,
        "is_dirty": bool(dirty_state),
    }


def classify_category(relative_path: Path) -> str:
    top_level = relative_path.parts[0] if relative_path.parts else "other"
    normalized_path = relative_path.as_posix().lower()

    if top_level == "architecture":
        return "reference"
    if top_level == "disconnected":
        return "troubleshooting"
    if top_level == "post_installation_configuration":
        if "/updating/" in normalized_path:
            return "upgrade"
        if "/troubleshooting/" in normalized_path:
            return "troubleshooting"
        return "operations"

    mapping = {
        "installing": "install",
        "updating": "upgrade",
        "upgrading": "upgrade",
        "networking": "networking",
        "security": "security",
        "storage": "storage",
        "backup_and_restore": "troubleshooting",
        "support": "troubleshooting",
        "observability": "troubleshooting",
    }
    return mapping.get(top_level, "other")


def build_default_attr_values(version_label: str) -> dict[str, str]:
    return {
        "product-title": "OpenShift Container Platform",
        "product-version": version_label,
    }


def replace_attrs(text: str, state: ParserState) -> str:
    def replace_match(match: re.Match[str]) -> str:
        key = match.group(1)
        if key == "context":
            return state.context_value
        if key in state.attr_values:
            return state.attr_values[key]
        return ""

    return re.sub(r"\{([^}]+)\}", replace_match, text)


def clean_inline_text(text: str, state: ParserState) -> str:
    text = replace_attrs(text, state)
    text = re.sub(r"xref:([^\[]+)\[([^\]]*)\]", r"\2", text)
    text = re.sub(r"link:([^\[]+)\[([^\]]*)\]", r"\2", text)
    text = re.sub(r"<<[^,>]+,([^>]+)>>", r"\1", text)
    text = text.replace("{nbsp}", " ")
    text = text.replace("`", "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def slugify(text: str) -> str:
    lowered = text.lower()
    lowered = re.sub(r"[^a-z0-9\s_-]", "", lowered)
    lowered = re.sub(r"[\s_]+", "-", lowered)
    lowered = re.sub(r"-{2,}", "-", lowered).strip("-")
    return lowered or "section"


def unique_anchor_id(preferred: str, used: dict[str, int]) -> str:
    base = preferred or "section"
    count = used.get(base, 0) + 1
    used[base] = count
    if count == 1:
        return base
    return f"{base}-{count}"


def parse_condition_tokens(raw_tokens: str) -> list[str]:
    return [token.strip() for token in raw_tokens.split(",") if token.strip()]


def parse_level_offset(options: str) -> int:
    match = LEVEL_OFFSET_RE.search(options)
    if not match:
        return 0
    return int(match.group(1))


def resolve_include_target(current_file: Path, include_target: str, source_root: Path) -> Path | None:
    candidate = (current_file.parent / include_target).resolve()
    if candidate.exists():
        return candidate
    root_candidate = (source_root / include_target).resolve()
    if root_candidate.exists():
        return root_candidate
    return None


def resolve_document_lines(
    source_file: Path,
    source_root: Path,
    state: ParserState,
    heading_offset: int = 0,
    include_stack: set[Path] | None = None,
) -> list[str]:
    include_stack = include_stack or set()
    if source_file in include_stack:
        return []

    include_stack.add(source_file)
    lines_out: list[str] = []
    condition_stack: list[bool] = []

    for raw_line in source_file.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = raw_line.strip()

        if ENDIF_RE.match(stripped):
            if condition_stack:
                condition_stack.pop()
            continue

        if eval_match := IFEVAL_CONTEXT_RE.match(stripped):
            condition_stack.append(state.context_value == eval_match.group(1))
            continue

        if ifdef_match := IFDEF_RE.match(stripped):
            tokens = parse_condition_tokens(ifdef_match.group(1))
            condition_stack.append(any(token in state.attrs for token in tokens))
            continue

        if ifndef_match := IFNDEF_RE.match(stripped):
            tokens = parse_condition_tokens(ifndef_match.group(1))
            condition_stack.append(not any(token in state.attrs for token in tokens))
            continue

        if condition_stack and not all(condition_stack):
            continue

        if attr_match := ATTR_RE.match(stripped):
            attr_name = attr_match.group(1)
            attr_value = attr_match.group(2).strip()
            if attr_name.endswith("!"):
                clean_name = attr_name[:-1]
                state.attrs.discard(clean_name)
                state.attr_values.pop(clean_name, None)
                continue
            if attr_name == "context":
                state.context_value = attr_value
                state.attrs.add("context")
                state.attr_values["context"] = attr_value
            else:
                state.attrs.add(attr_name)
                resolved_attr_value = replace_attrs(attr_value, state)
                state.attr_values[attr_name] = resolved_attr_value
            continue

        if stripped.startswith("//") or stripped == "toc::[]":
            continue

        if include_match := INCLUDE_RE.match(stripped):
            include_target = include_match.group(1)
            options = include_match.group(2)
            include_path = resolve_include_target(source_file, include_target, source_root)
            if not include_path:
                continue
            lines_out.extend(
                resolve_document_lines(
                    include_path,
                    source_root,
                    state,
                    heading_offset=heading_offset + parse_level_offset(options),
                    include_stack=include_stack.copy(),
                )
            )
            continue

        if id_match := ID_RE.match(stripped):
            resolved_id = replace_attrs(id_match.group(1), state)
            lines_out.append(f'[id="{resolved_id}"]')
            continue

        if heading_match := HEADING_RE.match(raw_line):
            new_level = max(1, min(6, len(heading_match.group(1)) + heading_offset))
            heading_title = clean_inline_text(heading_match.group(2), state)
            lines_out.append(f'{"=" * new_level} {heading_title}')
            continue

        lines_out.append(replace_attrs(raw_line.rstrip(), state))

    return lines_out


def build_sections(lines: list[str], fallback_title: str, document_id: str) -> list[RenderSection]:
    sections: list[RenderSection] = []
    hierarchy: list[str] = []
    pending_anchor: str | None = None
    used_anchors: dict[str, int] = {}

    def start_section(title: str, level: int, anchor_id: str) -> RenderSection:
        nonlocal hierarchy
        if len(hierarchy) < level:
            hierarchy.extend([""] * (level - len(hierarchy)))
        hierarchy = hierarchy[:level]
        hierarchy[level - 1] = title
        heading_hierarchy = [item for item in hierarchy if item]
        section_index = len(sections)
        section_id = stable_section_id(document_id, anchor_id, section_index)
        section = RenderSection(
            section_id=section_id,
            title=title,
            anchor_id=anchor_id,
            level=level,
            heading_hierarchy=heading_hierarchy,
            section_index=section_index,
        )
        sections.append(section)
        return section

    current_section: RenderSection | None = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current_section:
                current_section.body_lines.append("")
            continue

        if id_match := ID_RE.match(stripped):
            pending_anchor = slugify(id_match.group(1))
            continue

        if heading_match := HEADING_RE.match(stripped):
            title = heading_match.group(2).strip() or fallback_title
            level = len(heading_match.group(1))
            anchor_id = unique_anchor_id(pending_anchor or slugify(title), used_anchors)
            current_section = start_section(title, level, anchor_id)
            pending_anchor = None
            continue

        if current_section is None:
            current_section = start_section(
                fallback_title,
                1,
                unique_anchor_id(pending_anchor or slugify(fallback_title), used_anchors),
            )
            pending_anchor = None

        current_section.body_lines.append(line.rstrip())

    if not sections:
        anchor_id = unique_anchor_id(slugify(fallback_title), used_anchors)
        sections.append(
            RenderSection(
                section_id=stable_section_id(document_id, anchor_id, 0),
                title=fallback_title,
                anchor_id=anchor_id,
                level=1,
                heading_hierarchy=[fallback_title],
                section_index=0,
                body_lines=[],
            )
        )

    return sections


def render_section_lines_to_text(lines: list[str], state: ParserState) -> str:
    output_lines: list[str] = []
    in_code = False
    code_lines: list[str] = []
    pending_code_language = ""
    in_table = False
    table_lines: list[str] = []

    def flush_code() -> None:
        nonlocal code_lines
        if code_lines:
            output_lines.append("```")
            output_lines.extend(code_lines)
            output_lines.append("```")
            code_lines = []

    def flush_table() -> None:
        nonlocal table_lines
        if table_lines:
            output_lines.extend(table_lines)
            table_lines = []

    for raw_line in lines:
        stripped = raw_line.strip()

        if source_match := SOURCE_BLOCK_RE.match(stripped):
            pending_code_language = source_match.group(1) or ""
            continue

        if stripped == "----":
            if in_code:
                flush_code()
                in_code = False
            else:
                in_code = True
            continue

        if in_code:
            code_lines.append(raw_line.rstrip())
            continue

        if stripped == "|===":
            if in_table:
                flush_table()
                in_table = False
            else:
                in_table = True
            continue

        if in_table:
            table_lines.append(clean_inline_text(stripped, state))
            continue

        if stripped == "+":
            continue

        if stripped.startswith("[") and stripped.endswith("]"):
            if admonition_match := ADMONITION_RE.match(stripped):
                output_lines.append(f"{admonition_match.group(1).title()}:")
            continue

        if not stripped:
            output_lines.append("")
            continue

        output_lines.append(clean_inline_text(raw_line, state))

    flush_code()
    flush_table()
    text = "\n".join(output_lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def render_section_lines_to_html(lines: list[str], state: ParserState) -> str:
    html_parts: list[str] = []
    paragraph_lines: list[str] = []
    ul_items: list[str] = []
    ol_items: list[str] = []
    code_lines: list[str] = []
    table_lines: list[str] = []
    in_code = False
    in_table = False
    pending_code_language = ""

    def flush_paragraph() -> None:
        nonlocal paragraph_lines
        if paragraph_lines:
            text = clean_inline_text(" ".join(paragraph_lines), state)
            if text:
                html_parts.append(f"<p>{html.escape(text)}</p>")
            paragraph_lines = []

    def flush_ul() -> None:
        nonlocal ul_items
        if ul_items:
            html_parts.append("<ul>")
            html_parts.extend(f"<li>{html.escape(item)}</li>" for item in ul_items)
            html_parts.append("</ul>")
            ul_items = []

    def flush_ol() -> None:
        nonlocal ol_items
        if ol_items:
            html_parts.append("<ol>")
            html_parts.extend(f"<li>{html.escape(item)}</li>" for item in ol_items)
            html_parts.append("</ol>")
            ol_items = []

    def flush_code() -> None:
        nonlocal code_lines
        if code_lines:
            class_attr = f' class="language-{pending_code_language}"' if pending_code_language else ""
            payload = html.escape("\n".join(code_lines))
            html_parts.append(f"<pre><code{class_attr}>{payload}</code></pre>")
            code_lines = []

    def flush_table() -> None:
        nonlocal table_lines
        if table_lines:
            payload = html.escape("\n".join(table_lines))
            html_parts.append(f'<pre class="table">{payload}</pre>')
            table_lines = []

    def flush_all() -> None:
        flush_paragraph()
        flush_ul()
        flush_ol()

    for raw_line in lines:
        stripped = raw_line.strip()

        if source_match := SOURCE_BLOCK_RE.match(stripped):
            pending_code_language = (source_match.group(1) or "").strip()
            continue

        if stripped == "----":
            flush_all()
            if in_code:
                flush_code()
                in_code = False
                pending_code_language = ""
            else:
                in_code = True
            continue

        if in_code:
            code_lines.append(raw_line.rstrip())
            continue

        if stripped == "|===":
            flush_all()
            if in_table:
                flush_table()
                in_table = False
            else:
                in_table = True
            continue

        if in_table:
            table_lines.append(clean_inline_text(stripped, state))
            continue

        if stripped == "+":
            continue

        if admonition_match := ADMONITION_RE.match(stripped):
            flush_all()
            html_parts.append(f'<p class="admonition-label">{html.escape(admonition_match.group(1).title())}</p>')
            continue

        if stripped.startswith("[") and stripped.endswith("]"):
            continue

        if not stripped:
            flush_all()
            continue

        if stripped.startswith("* "):
            flush_paragraph()
            flush_ol()
            ul_items.append(clean_inline_text(stripped[2:], state))
            continue

        if stripped.startswith(". "):
            flush_paragraph()
            flush_ul()
            ol_items.append(clean_inline_text(stripped[2:], state))
            continue

        flush_ul()
        flush_ol()
        paragraph_lines.append(stripped)

    flush_all()
    flush_code()
    flush_table()
    return "\n".join(html_parts)


def render_html_document(
    title: str,
    source_path: str,
    source_url: str,
    sections: list[RenderSection],
    state: ParserState,
) -> str:
    section_markup: list[str] = []
    for section in sections:
        heading_tag = f"h{min(max(section.level, 1), 6)}"
        body_markup = render_section_lines_to_html(section.body_lines, state)
        section_markup.append(
            "\n".join(
                [
                    f'<section class="doc-section" data-section-id="{html.escape(section.section_id)}">',
                    f'<{heading_tag} id="{html.escape(section.anchor_id)}">{html.escape(section.title)}</{heading_tag}>',
                    body_markup,
                    "</section>",
                ]
            )
        )

    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '  <meta charset="utf-8">',
            f"  <title>{html.escape(title)}</title>",
            "  <style>",
            "    body { font-family: Segoe UI, Arial, sans-serif; max-width: 960px; margin: 0 auto; padding: 32px; line-height: 1.6; color: #1f2933; }",
            "    h1, h2, h3, h4, h5, h6 { margin-top: 1.5em; color: #102a43; }",
            "    pre { background: #f5f7fa; padding: 12px; overflow-x: auto; border-radius: 6px; }",
            "    code { font-family: Consolas, monospace; }",
            "    .doc-meta { color: #52606d; margin-bottom: 24px; }",
            "    .doc-section { margin-bottom: 24px; }",
            "    .admonition-label { font-weight: 700; color: #9f1239; margin-bottom: 0; }",
            "    .table { white-space: pre-wrap; }",
            "  </style>",
            "</head>",
            "<body>",
            f"  <h1>{html.escape(title)}</h1>",
            f'  <p class="doc-meta">Source path: {html.escape(source_path)}<br>Source URL: <a href="{html.escape(source_url)}">{html.escape(source_url)}</a></p>',
            *section_markup,
            "</body>",
            "</html>",
        ]
    )


def build_normalized_payload(title: str, relative_path: Path, viewer_url: str, sections: list[RenderSection], state: ParserState) -> str:
    blocks = [
        f"Title: {title}",
        f"Source Path: {relative_path.as_posix()}",
        f"Viewer URL: {viewer_url}",
        "",
    ]
    for section in sections:
        heading_path = " > ".join(section.heading_hierarchy)
        blocks.append(f"[Section] {heading_path}")
        section_text = render_section_lines_to_text(section.body_lines, state)
        if section_text:
            blocks.append(section_text)
        blocks.append("")
    payload = "\n".join(blocks)
    payload = re.sub(r"\n{3,}", "\n\n", payload)
    return payload.strip() + "\n"


def write_text_file(target: Path, payload: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(payload, encoding="utf-8")


def section_manifest(section: RenderSection, viewer_url: str) -> dict[str, object]:
    return {
        "section_id": section.section_id,
        "section_title": section.title,
        "section_anchor": section.anchor_id,
        "heading_hierarchy": section.heading_hierarchy,
        "level": section.level,
        "section_index": section.section_index,
        "viewer_url": viewer_url,
    }


def normalize_documents(args: argparse.Namespace) -> int:
    profile = resolve_source_profile(args)
    source_root = Path(profile["source_root"]).resolve()
    source_id = str(profile["source_id"])
    version_label = str(profile["version_label"])
    include_dirs = list(profile["include_dirs"])
    exclude_dirs = set(profile["exclude_dirs"])
    exclude_prefixes = tuple(profile["exclude_prefixes"])
    exclude_fragments = list(profile["exclude_fragments"])
    lineage = detect_source_lineage(source_root, str(profile["declared_git_ref"]))
    if not args.allow_ref_mismatch and not lineage["git_ref_matches_profile"]:
        raise SystemExit(
            "Resolved source profile ref does not match the checked-out source tree. "
            f"profile={profile['profile_id'] or 'manual'}, declared_ref={lineage['declared_git_ref']}, "
            f"detected_ref={lineage['detected_git_ref']}"
        )

    default_output_dir = Path("./data/normalized/openshift-docs-p0")
    default_html_dir = Path("./data/views/openshift-docs-p0")
    default_manifest_out = Path("./data/manifests/generated/openshift-docs-p0.json")
    output_dir = (
        Path("./data/normalized") / source_id if args.output_dir == default_output_dir else args.output_dir
    ).resolve()
    html_dir = (
        Path("./data/views") / source_id if args.html_dir == default_html_dir else args.html_dir
    ).resolve()
    manifest_out = (
        Path("./data/manifests/generated") / f"{source_id}.json" if args.manifest_out == default_manifest_out else args.manifest_out
    ).resolve()
    collected_at = datetime.now(timezone.utc).isoformat()

    if not source_root.exists():
        raise SystemExit(f"source root does not exist: {source_root}")

    source_files = collect_source_files(source_root, include_dirs)
    documents: list[NormalizedDocument] = []
    skipped = Counter()

    if not args.dry_run:
        shutil.rmtree(output_dir, ignore_errors=True)
        shutil.rmtree(html_dir, ignore_errors=True)

    for source_file in source_files:
        relative_path = source_file.relative_to(source_root)
        skip_reason = skip_reason_for_path(relative_path, exclude_fragments, exclude_dirs, exclude_prefixes)
        if skip_reason:
            skipped[skip_reason] += 1
            continue

        parser_state = ParserState(attr_values=build_default_attr_values(version_label))
        resolved_lines = resolve_document_lines(source_file, source_root, parser_state)
        title = source_file.stem
        for line in resolved_lines:
            heading_match = HEADING_RE.match(line.strip())
            if heading_match:
                title = clean_inline_text(heading_match.group(2), parser_state) or title
                break

        document_id = stable_document_id(relative_path)
        sections = build_sections(resolved_lines, title, document_id)
        viewer_url = build_viewer_url(source_id, relative_path)
        normalized_payload = build_normalized_payload(title, relative_path, viewer_url, sections, parser_state)
        checksum = sha256_text(normalized_payload)
        source_url_ref = str(lineage["detected_git_commit"] or lineage["declared_git_ref"] or "main")

        normalized_path = output_dir / relative_path.with_suffix(".txt")
        html_path = html_dir / relative_path.with_suffix(".html")

        document = NormalizedDocument(
            document_id=document_id,
            title=title,
            source_id=source_id,
            source_type=str(profile["source_type"]),
            source_mirror_id=str(profile["mirror_id"]),
            source_profile_id=str(profile["profile_id"]),
            source_url=build_source_url(relative_path, source_url_ref, str(profile["source_url_base"])),
            source_git_ref=str(lineage["declared_git_ref"]),
            source_git_commit=str(lineage["detected_git_commit"]),
            local_path=str(source_file),
            normalized_path=str(normalized_path),
            html_path=str(html_path),
            viewer_url=viewer_url,
            product=str(profile["product"]),
            version=version_label,
            target_minor=(str(profile["target_minor"]) if profile["target_minor"] else None),
            category=classify_category(relative_path),
            language=str(profile["language"]),
            trust_level=str(profile["trust_level"]),
            collected_at=collected_at,
            checksum=checksum,
            top_level_dir=relative_path.parts[0],
            section_count=len(sections),
            sections=[section_manifest(section, viewer_url) for section in sections],
        )
        documents.append(document)

        if not args.dry_run:
            write_text_file(normalized_path, normalized_payload)
            html_payload = render_html_document(title, relative_path.as_posix(), document.source_url, sections, parser_state)
            write_text_file(html_path, html_payload)

    manifest = {
        "manifest_id": f"{source_id}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "source_root": str(source_root),
        "source_id": source_id,
        "collected_at": collected_at,
        "version_label": version_label,
        "source_profile": {
            "profile_id": profile["profile_id"],
            "purpose": profile["purpose"],
            "corpus_scope": profile["corpus_scope"],
            "mirror_id": profile["mirror_id"],
            "catalog_path": profile["catalog_path"],
            "active_config_path": profile["active_config_path"],
        },
        "target_release": {
            "target_minor": profile["target_minor"],
            "declared_git_ref": lineage["declared_git_ref"],
            "version_label": version_label,
        },
        "source_lineage": lineage,
        "collection_scope": {
            "include_dirs": include_dirs,
            "exclude_dirs": sorted(exclude_dirs),
            "exclude_prefixes": list(exclude_prefixes),
            "exclude_path_fragments": exclude_fragments,
        },
        "scanned_adoc_count": len(source_files),
        "document_count": len(documents),
        "top_level_counts": dict(sorted(Counter(doc.top_level_dir for doc in documents).items())),
        "category_counts": dict(sorted(Counter(doc.category for doc in documents).items())),
        "skipped_counts": dict(sorted(skipped.items())),
        "documents": [asdict(document) for document in documents],
    }

    if args.dry_run:
        if args.show_documents:
            print(json.dumps(manifest, indent=2))
            return 0

        summary = {key: value for key, value in manifest.items() if key != "documents"}
        summary["sample_documents"] = [
            {
                "title": document.title,
                "category": document.category,
                "top_level_dir": document.top_level_dir,
                "viewer_url": document.viewer_url,
                "section_count": document.section_count,
                "local_path": document.local_path,
            }
            for document in documents[:15]
        ]
        print(json.dumps(summary, indent=2))
        return 0

    manifest_out.parent.mkdir(parents=True, exist_ok=True)
    manifest_out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[ok] normalized {len(documents)} documents")
    print(f"[ok] html views written to {html_dir}")
    print(f"[ok] manifest written to {manifest_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(normalize_documents(parse_args()))
