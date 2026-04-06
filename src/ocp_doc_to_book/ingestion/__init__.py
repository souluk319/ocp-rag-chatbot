WEB_CAPTURE_GUIDE = (
    "Prefer html-single acquisition for documentation websites so chapter-level source mapping "
    "and source-view rendering stay aligned."
)

from .pdf import resolve_pdf_capture
from .web import resolve_web_capture_url

__all__ = [
    "WEB_CAPTURE_GUIDE",
    "resolve_pdf_capture",
    "resolve_web_capture_url",
]
