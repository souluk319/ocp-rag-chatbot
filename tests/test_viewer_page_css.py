from play_book_studio.app.viewer_page_layout import _viewer_page_css


def test_viewer_page_css_supports_wrapped_code_blocks() -> None:
    _viewer_page_css.cache_clear()
    css = _viewer_page_css()

    assert ".code-block.overflow-toggle.is-wrapped pre," in css
    assert ".code-block.overflow-wrap pre {" in css
    assert "white-space: pre-wrap;" in css
    assert "overflow-x: hidden;" in css
    assert "overflow-wrap: anywhere;" in css
    assert ".code-block.overflow-toggle.is-wrapped code," in css
    assert ".code-block.overflow-wrap code {" in css
