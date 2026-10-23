"""Tests for the page / web-part handoff detector."""

import unittest

from office365.migration.sharepoint.pages import (
    PAGE_LIBRARY_TEMPLATE,
    detect_page_handoff,
    page_handoff_note,
)

# A modern canvas control blob as SharePoint serializes it (HTML-encoded JSON).
_WEB_PART_CONTROL = 'data-sp-controldata="{&quot;controlType&quot;:4}"'
_SECTION_CONTROL = 'data-sp-controldata="{&quot;controlType&quot;:3}"'


class _Items:
    def __init__(self, items):
        self._items = list(items)
        self.select_calls: list[tuple[str, ...]] = []

    def get(self):
        return self

    def select(self, fields):
        self.select_calls.append(tuple(fields))
        return self

    def execute_query(self):
        return list(self._items)


class _Item:
    def __init__(self, **properties):
        self.properties = properties


class _List:
    def __init__(self, title, base_template=100, hidden=False, items=None):
        self.title = title
        self.base_template = base_template
        self.hidden = hidden
        self.items = _Items(items or [])


def _page(name, canvas="", wiki=""):
    return _Item(FileLeafRef=name, CanvasContent1=canvas, WikiField=wiki)


class TestDetectPageHandoff(unittest.TestCase):
    def test_note_truncates_long_page_lists(self):
        items = [_page(f"P{i}.aspx") for i in range(7)]
        library = _List("Site Pages", base_template=PAGE_LIBRARY_TEMPLATE, items=items)

        note = page_handoff_note(detect_page_handoff([library]))

        self.assertIsNotNone(note)
        self.assertIn("+2 more", note)


if __name__ == "__main__":
    unittest.main()
