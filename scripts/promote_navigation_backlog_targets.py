from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

INPUT_PATH = ROOT / "data" / "wiki_relations" / "navigation_backlog.json"
OUTPUT_JSON_PATH = ROOT / "data" / "wiki_relations" / "priority_targets.json"
OUTPUT_MD_PATH = ROOT / "data" / "wiki_relations" / "priority_targets.md"
OUTPUT_REPORT_PATH = ROOT / "reports" / "build_logs" / "priority_targets_report.json"


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return payload if isinstance(payload, dict) else {}


def _priority_entries(backlog: dict[str, Any]) -> list[dict[str, Any]]:
    entries = backlog.get("entries") if isinstance(backlog.get("entries"), list) else []
    by_id: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        signal_id = str(entry.get("signal_id") or "").strip()
        if not signal_id:
            continue
        by_id[signal_id] = entry

    priorities: list[dict[str, Any]] = []

    etcd = by_id.get("entity:etcd")
    if etcd:
        priorities.append(
            {
                "target_id": "wiki-target-etcd-density",
                "title": "etcd Hub Densification",
                "priority": 1,
                "why_now": "추천질문과 관련 탐색에서 가장 강한 허브 재진입 신호가 etcd 축으로 모인다.",
                "primary_signal": etcd,
                "expansion_goal": "etcd 허브를 backup, restore, control plane recovery, monitoring signal 확인 경로까지 확장한다.",
                "deliverables": [
                    "etcd 허브 related books 확장",
                    "etcd 관련 troubleshooting book 연결",
                    "etcd 허브 backlink 보강",
                ],
            }
        )

    machine_query = by_id.get("query:복원-후-machine-configuration은-왜-같이-봐야-하는지-알려줘")
    machine_book = by_id.get("book:machine-configuration")
    if machine_query or machine_book:
        priorities.append(
            {
                "target_id": "wiki-target-machine-config-recovery-bridge",
                "title": "Machine Configuration Recovery Bridge",
                "priority": 2,
                "why_now": "복원 이후 Machine Configuration을 같이 봐야 한다는 신호가 반복적으로 등장한다.",
                "primary_signal": machine_query or machine_book,
                "supporting_signal": machine_book or machine_query,
                "expansion_goal": "Backup and Restore와 Machine Configuration 사이의 운영 분기와 후속 확인 경로를 별도 bridge book 또는 relation으로 고정한다.",
                "deliverables": [
                    "복원 후 MCO 확인 경로 정리",
                    "machine_configuration 허브/문서 backlink 강화",
                    "chat related links에 복구 후속 점검 경로 고정",
                ],
            }
        )

    monitoring_query = by_id.get("query:백업-후-monitoring에서는-어떤-신호를-먼저-확인해야-해?")
    proxy = by_id.get("entity:cluster-wide-proxy")
    if monitoring_query or proxy:
        priorities.append(
            {
                "target_id": "wiki-target-post-action-verification",
                "title": "Post-Action Verification Path",
                "priority": 3,
                "why_now": "실행 이후 무엇을 먼저 검증해야 하는지에 대한 후속 질문이 반복되고 있다.",
                "primary_signal": monitoring_query or proxy,
                "supporting_signal": proxy or monitoring_query,
                "expansion_goal": "복구/설치/프록시 변경 이후 Monitoring과 검증 문서를 묶는 후속 점검 위키 경로를 만든다.",
                "deliverables": [
                    "Monitoring verification path relation 추가",
                    "post-action verify 중심 북 후보 정의",
                    "추천질문을 verification path로 재고정",
                ],
            }
        )

    return priorities


def _build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Priority Wiki Targets",
        "",
        "현재 navigation backlog 기준 다음 위키 확장 타깃 3개입니다.",
        "",
    ]
    for item in payload.get("targets", []):
        if not isinstance(item, dict):
            continue
        lines.extend(
            [
                f"## P{item['priority']}. {item['title']}",
                "",
                f"- why_now: {item['why_now']}",
                f"- expansion_goal: {item['expansion_goal']}",
                "- deliverables:",
            ]
        )
        for deliverable in item.get("deliverables", []):
            lines.append(f"  - {deliverable}")
        primary = item.get("primary_signal") if isinstance(item.get("primary_signal"), dict) else {}
        if primary:
            lines.append(f"- primary_signal: `{primary.get('signal_id', '')}` · count=`{primary.get('count', 0)}`")
        supporting = item.get("supporting_signal") if isinstance(item.get("supporting_signal"), dict) else {}
        if supporting:
            lines.append(f"- supporting_signal: `{supporting.get('signal_id', '')}` · count=`{supporting.get('count', 0)}`")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def main() -> int:
    backlog = _read_json(INPUT_PATH)
    targets = _priority_entries(backlog)
    payload = {
        "status": "ok",
        "source_backlog_path": str(INPUT_PATH),
        "target_count": len(targets),
        "targets": targets,
    }
    OUTPUT_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    OUTPUT_MD_PATH.write_text(_build_markdown(payload), encoding="utf-8")
    OUTPUT_REPORT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
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
