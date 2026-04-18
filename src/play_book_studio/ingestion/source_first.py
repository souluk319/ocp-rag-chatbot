from __future__ import annotations

from pathlib import Path


SOURCE_REPO_URL = "https://github.com/openshift/openshift-docs"
SOURCE_BRANCH = "enterprise-4.20"
SOURCE_MIRROR_DIRNAME = "openshift-docs-enterprise-4.20"

MANUAL_PATH_ALIASES: dict[str, str] = {
    "architecture": "architecture/index.adoc",
    "authentication_and_authorization": "authentication/index.adoc",
    "backup_and_restore": "backup_and_restore/index.adoc",
    "cli_tools": "cli_reference/index.adoc",
    "disconnected_environments": "disconnected/index.adoc",
    "etcd": "etcd/etcd-overview.adoc",
    "images": "openshift_images/index.adoc",
    "installing_on_any_platform": "installing/overview/index.adoc",
    "installation_overview": "installing/overview/index.adoc",
    "machine_configuration": "machine_configuration/index.adoc",
    "machine_management": "machine_management/index.adoc",
    "monitoring": "observability/monitoring/about-ocp-monitoring.adoc",
    "nodes": "nodes/index.adoc",
    "observability_overview": "observability/overview/index.adoc",
    "operators": "operators/index.adoc",
    "postinstallation_configuration": "post_installation_configuration/index.adoc",
    "registry": "registry/index.adoc",
    "security_and_compliance": "security/index.adoc",
    "storage": "storage/index.adoc",
    "support": "support/index.adoc",
    "updating_clusters": "updating/index.adoc",
    "web_console": "web_console/index.adoc",
}


def source_mirror_root(root_dir: Path) -> Path:
    return root_dir / "tmp_source" / SOURCE_MIRROR_DIRNAME


def repo_path_candidates(root_dir: Path, slug: str) -> list[Path]:
    mirror_root = source_mirror_root(root_dir)
    candidates: list[Path] = []
    alias = MANUAL_PATH_ALIASES.get(slug)
    if alias:
        candidates.append(mirror_root / alias)
    candidates.extend(
        [
            mirror_root / slug / "index.adoc",
            mirror_root / slug.replace("_", "-") / "index.adoc",
        ]
    )
    return candidates


def resolve_repo_path(root_dir: Path, slug: str) -> Path | None:
    for candidate in repo_path_candidates(root_dir, slug):
        if candidate.exists() and candidate.is_file():
            return candidate.resolve()
    return None


def resolve_repo_relative_path(root_dir: Path, slug: str) -> str:
    resolved = resolve_repo_path(root_dir, slug)
    if resolved is None:
        return ""
    mirror_root = source_mirror_root(root_dir).resolve()
    try:
        return str(resolved.relative_to(mirror_root)).replace("\\", "/")
    except ValueError:
        return ""
