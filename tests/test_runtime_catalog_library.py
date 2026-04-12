from __future__ import annotations

from play_book_studio.ingestion.runtime_catalog_library import (
    _retain_non_official_non_derived_playbook_rows,
    _retain_non_official_rows,
)


def test_retain_non_official_rows_keeps_manual_synthesis() -> None:
    rows = [
        {"book_slug": "overview", "source_type": "official_doc"},
        {"book_slug": "etcd", "source_type": "manual_synthesis"},
        {"book_slug": "custom", "source_type": "customer_pack"},
    ]

    retained = _retain_non_official_rows(rows)

    assert [row["book_slug"] for row in retained] == ["etcd", "custom"]


def test_retain_non_official_non_derived_playbook_rows_drops_official_and_derived() -> None:
    rows = [
        {
            "book_slug": "overview",
            "source_metadata": {"source_type": "official_doc"},
        },
        {
            "book_slug": "etcd",
            "source_metadata": {"source_type": "manual_synthesis"},
        },
        {
            "book_slug": "overview_topic_playbook",
            "source_metadata": {"source_type": "topic_playbook"},
        },
    ]

    retained = _retain_non_official_non_derived_playbook_rows(rows)

    assert [row["book_slug"] for row in retained] == ["etcd"]
