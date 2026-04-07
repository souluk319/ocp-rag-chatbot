from __future__ import annotations

from ocp_rag_part3.models import Citation


def _citation_href(citation: Citation) -> str:
    viewer_path = (citation.viewer_path or "").strip()
    if viewer_path:
        return viewer_path
    if citation.anchor:
        return f"{citation.source_url}#{citation.anchor}"
    return citation.source_url


def _humanize_book_slug(book_slug: str) -> str:
    return " ".join(part for part in str(book_slug or "").replace("_", " ").split())


def _core_pack_payload(*, version: str = "4.20") -> dict[str, str]:
    version_token = version.replace(".", "-")
    return {
        "source_collection": "core",
        "pack_id": f"openshift-{version_token}-core",
        "pack_label": f"OpenShift {version} Core Pack",
        "inferred_product": "openshift",
        "inferred_version": version,
    }

