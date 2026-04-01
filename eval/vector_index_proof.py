from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.vector_index import VectorIndex, VectorRecord


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a proof report for the in-repo vector index implementation."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT
        / "data"
        / "manifests"
        / "generated"
        / "vector-index-proof.json",
    )
    return parser.parse_args()


def sample_records() -> list[VectorRecord]:
    return [
        VectorRecord(
            chunk_id="chunk-firewall-001",
            document_id="doc-firewall",
            document_path="installing/install_config/configuring-firewall.adoc",
            section_id="section-firewall",
            section_title="Configuring your firewall",
            viewer_url="/viewer/ocp/installing/install_config/configuring-firewall",
            embedding=(0.92, 0.05, 0.01, 0.0),
            metadata={"category": "install", "top_level_dir": "installing"},
        ),
        VectorRecord(
            chunk_id="chunk-update-001",
            document_id="doc-update",
            document_path="updating/preparing_for_updates/updating-cluster-prepare.adoc",
            section_id="section-update",
            section_title="Preparing to perform an update",
            viewer_url="/viewer/ocp/updating/preparing_for_updates/updating-cluster-prepare",
            embedding=(0.08, 0.88, 0.02, 0.01),
            metadata={"category": "upgrade", "top_level_dir": "updating"},
        ),
        VectorRecord(
            chunk_id="chunk-disconnected-001",
            document_id="doc-disconnected",
            document_path="disconnected/about-installing-oc-mirror-v2.adoc",
            section_id="section-disconnected",
            section_title="About installing oc-mirror v2",
            viewer_url="/viewer/ocp/disconnected/about-installing-oc-mirror-v2",
            embedding=(0.05, 0.03, 0.91, 0.0),
            metadata={"category": "disconnected", "top_level_dir": "disconnected"},
        ),
    ]


def main() -> None:
    args = parse_args()
    index = VectorIndex(dimensions=4)
    records = sample_records()
    index.extend(records)

    stored_path = (
        REPO_ROOT / "data" / "manifests" / "generated" / "vector-index-sample.json"
    )
    index.save(stored_path)
    reloaded = VectorIndex.load(stored_path)

    firewall_results = reloaded.search((0.95, 0.03, 0.01, 0.0), top_k=2)
    update_results = reloaded.search((0.03, 0.97, 0.01, 0.0), top_k=2)

    report = {
        "trace_version": "vector-index-proof-v1",
        "dimensions": reloaded.dimensions,
        "record_count": reloaded.size,
        "storage_path": str(stored_path.relative_to(REPO_ROOT)),
        "firewall_query": [item.to_dict() for item in firewall_results],
        "update_query": [item.to_dict() for item in update_results],
        "overall_pass": (
            reloaded.size == 3
            and firewall_results[0].document_path
            == "installing/install_config/configuring-firewall.adoc"
            and update_results[0].document_path
            == "updating/preparing_for_updates/updating-cluster-prepare.adoc"
        ),
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
