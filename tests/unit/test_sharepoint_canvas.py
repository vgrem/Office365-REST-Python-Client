"""Tests for the modern-page canvas parser and ``SitePage.web_part_count``."""

from office365.sharepoint.publishing.pages.canvas import (
    WEB_PART_CONTROL_TYPE,
    count_web_parts,
    parse_canvas_controls,
)
from office365.sharepoint.publishing.pages.page import SitePage

#: One canvas control, HTML-escaped exactly as SharePoint serializes it.
_CONTROL = '<div data-sp-controldata="{&quot;controlType&quot;:%d}">%s</div>'


def _canvas(*control_types):
    return "".join(_CONTROL % (control_type, "") for control_type in control_types)


def test_no_canvas_has_no_controls():
    assert parse_canvas_controls(None) == []
    assert parse_canvas_controls("") == []
    assert count_web_parts(None) == 0
    assert count_web_parts("<div>classic wiki html</div>") == 0


def test_skips_malformed_and_non_object_blobs():
    canvas = (
        '<div data-sp-controldata="{&quot;controlType&quot;:4}"></div>'
        '<div data-sp-controldata="{not json}"></div>'
        '<div data-sp-controldata="[1, 2]"></div>'
    )
    controls = parse_canvas_controls(canvas)
    assert [control.control_type for control in controls] == [WEB_PART_CONTROL_TYPE]


def test_site_page_counts_web_parts_in_its_canvas():
    page = SitePage(None)
    assert page.web_part_count == 0
    page.set_property("CanvasContent1", _canvas(4, 4, 3))
    assert page.web_part_count == 2  # noqa: PLR2004
