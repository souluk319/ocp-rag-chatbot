from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from play_book_studio.config.settings import load_settings
from play_book_studio.app import source_books


@dataclass(slots=True)
class Candidate:
    slug: str
    title: str
    source_trial_path: str
    promotion_strategy: str
    source_kind: str


WAVE1_CANDIDATES: tuple[Candidate, ...] = (
    Candidate(
        slug="backup_and_restore",
        title="Backup and Restore",
        source_trial_path="tests/reader_grade_pipeline_trials/backup_and_restore/14_asciidoc_plus_12_tone/output.md",
        promotion_strategy="asciidoc_source_first_plus_12_tone",
        source_kind="official_source_repo",
    ),
    Candidate(
        slug="installing_on_any_platform",
        title="Installing on Any Platform",
        source_trial_path="tests/reader_grade_pipeline_trials/installing_on_any_platform/14_asciidoc_plus_12_tone/output.md",
        promotion_strategy="asciidoc_source_first_plus_12_tone",
        source_kind="official_source_repo",
    ),
    Candidate(
        slug="machine_configuration",
        title="Machine Configuration",
        source_trial_path="tests/reader_grade_pipeline_trials/machine_configuration/14_asciidoc_plus_12_tone/output.md",
        promotion_strategy="asciidoc_source_first_plus_12_tone",
        source_kind="official_source_repo",
    ),
    Candidate(
        slug="monitoring_alerts_admin",
        title="Monitoring Alerts Admin Book",
        source_trial_path="tests/reader_grade_pipeline_trials/monitoring/14_alerts_admin_book/output.md",
        promotion_strategy="asciidoc_source_first_task_split_book",
        source_kind="official_source_repo",
    ),
    Candidate(
        slug="monitoring_metrics_admin",
        title="Monitoring Metrics Admin Book",
        source_trial_path="tests/reader_grade_pipeline_trials/monitoring/15_metrics_admin_book/output.md",
        promotion_strategy="asciidoc_source_first_task_split_book",
        source_kind="official_source_repo",
    ),
    Candidate(
        slug="monitoring_troubleshooting",
        title="Monitoring Troubleshooting Book",
        source_trial_path="tests/reader_grade_pipeline_trials/monitoring/16_troubleshooting_book/output.md",
        promotion_strategy="asciidoc_source_first_task_split_book",
        source_kind="official_source_repo",
    ),
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _candidate_output_root(settings_root: Path) -> Path:
    return settings_root / "data" / "gold_candidate_books" / "wave1"


def _report_path(settings_root: Path) -> Path:
    return settings_root / "reports" / "build_logs" / "wave1_gold_candidate_promotion_report.json"


def _catalog_path(settings_root: Path) -> Path:
    return settings_root / "data" / "gold_candidate_books" / "wave1_catalog.md"


def _manifest_path(settings_root: Path) -> Path:
    return settings_root / "data" / "gold_candidate_books" / "wave1_manifest.json"


def _catalog_markdown(created_at: str, promoted: list[dict[str, str]]) -> str:
    lines = [
        "# Wave 1 Gold Candidate Catalog",
        "",
        "## 현재 판단",
        "",
        "이 카탈로그는 Wave 1에서 현재 gold 승격 기준선으로 채택한 reader-grade md만 모아둔 것이다.",
        "",
        f"- generated_at_utc: `{created_at}`",
        "",
        "## Entries",
        "",
    ]
    for item in promoted:
        lines.extend(
            [
                f"### `{item['slug']}`",
                "",
                f"- title: `{item['title']}`",
                f"- promoted_path: [{Path(item['promoted_path']).name}]({item['promoted_path']})",
                f"- source_trial_path: [{Path(item['source_trial_path']).name}]({item['source_trial_path']})",
                f"- promotion_strategy: `{item['promotion_strategy']}`",
                f"- source_kind: `{item['source_kind']}`",
                "",
            ]
        )
    return "\n".join(lines).strip() + "\n"


def main() -> int:
    settings = load_settings(ROOT)
    out_root = _candidate_output_root(settings.root_dir)
    out_root.mkdir(parents=True, exist_ok=True)
    (_report_path(settings.root_dir)).parent.mkdir(parents=True, exist_ok=True)
    (_manifest_path(settings.root_dir)).parent.mkdir(parents=True, exist_ok=True)

    created_at = _utc_now()
    promoted: list[dict[str, str]] = []
    for candidate in WAVE1_CANDIDATES:
        source_path = settings.root_dir / candidate.source_trial_path
        if not source_path.exists():
            raise FileNotFoundError(f"Missing source trial output: {source_path}")
        target_path = out_root / f"{candidate.slug}.md"
        target_path.write_text(source_path.read_text(encoding="utf-8"), encoding="utf-8")
        promoted.append(
            {
                "slug": candidate.slug,
                "title": candidate.title,
                "source_trial_path": str(source_path),
                "promoted_path": str(target_path),
                "promotion_strategy": candidate.promotion_strategy,
                "source_kind": candidate.source_kind,
            }
        )

    manifest_payload = {
        "generated_at_utc": created_at,
        "candidate_count": len(promoted),
        "promotion_group": "wave1_gold_candidates",
        "entries": promoted,
    }
    _manifest_path(settings.root_dir).write_text(
        json.dumps(manifest_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    _report_path(settings.root_dir).write_text(
        json.dumps(
            {
                "generated_at_utc": created_at,
                "status": "ok",
                "count": len(promoted),
                "output_root": str(out_root),
                "manifest_path": str(_manifest_path(settings.root_dir)),
                "catalog_path": str(_catalog_path(settings.root_dir)),
                "entries": promoted,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    _catalog_path(settings.root_dir).write_text(
        _catalog_markdown(created_at, promoted),
        encoding="utf-8",
    )
    wiki_relations_dir = settings.root_dir / "data" / "wiki_relations"
    wiki_relations_dir.mkdir(parents=True, exist_ok=True)
    (wiki_relations_dir / "entity_hubs.json").write_text(
        json.dumps(source_books._entity_hubs(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (wiki_relations_dir / "chat_navigation_aliases.json").write_text(
        json.dumps(source_books._chat_navigation_aliases(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (wiki_relations_dir / "candidate_relations.json").write_text(
        json.dumps(source_books._candidate_relations(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": "ok",
                "count": len(promoted),
                "output_root": str(out_root),
                "manifest_path": str(_manifest_path(settings.root_dir)),
                "catalog_path": str(_catalog_path(settings.root_dir)),
                "wiki_relations_dir": str(wiki_relations_dir),
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
