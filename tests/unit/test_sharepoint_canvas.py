"""Tests for the modern-page canvas parser and ``SitePage.web_part_count``."""

from office365.sharepoint.publishing.pages.canvas import (
    WEB_PART_CONTROL_TYPE,
    parse_canvas_controls,
)

#: One canvas control, HTML-escaped exactly as SharePoint serializes it.
_CONTROL = '<div data-sp-controldata="{&quot;controlType&quot;:%d}">%s</div>'


def test_skips_malformed_and_non_object_blobs():
    canvas = (
        '<div data-sp-controldata="{&quot;controlType&quot;:4}"></div>'
        '<div data-sp-controldata="{not json}"></div>'
        '<div data-sp-controldata="[1, 2]"></div>'
    )
    controls = parse_canvas_controls(canvas)
    assert [control.control_type for control in controls] == [WEB_PART_CONTROL_TYPE]
