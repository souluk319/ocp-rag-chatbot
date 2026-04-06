CANONICAL_SECTION_FIELDS = (
    "book_slug",
    "book_title",
    "heading",
    "section_level",
    "section_path",
    "anchor",
    "source_url",
    "viewer_path",
    "text",
)

from .service import DocToBookNormalizeService

__all__ = [
    "CANONICAL_SECTION_FIELDS",
    "DocToBookNormalizeService",
]
