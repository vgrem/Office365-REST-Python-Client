"""Tests for the modern site page copy (create + fill + publish + verify)."""

import unittest

from office365.migration.sharepoint.pages import (
    DUPLICATE_OVERWRITE,
    DUPLICATE_RENAME,
    DUPLICATE_SKIP,
    PAGE_LIBRARY_TEMPLATE,
    PagePayload,
    apply_page_payload,
    capture_site_pages,
    copy_site_pages,
    detect_page_handoff,
    is_modern_page,
    page_handoff_note,
    verify_page_copy,
)

# A modern site page content type (inherited from the Site Page base content type).
_SITE_PAGE_CONTENT_TYPE = "0x0101009D1CB255DA76424F860D91F20E6C4118005E10E40F8E37D94AB983A0181120EFFC"
_WIKI_CONTENT_TYPE = "0x010108"

_WEB_PART_CONTROL = 'data-sp-controldata="{&quot;controlType&quot;:4}"'


class _PageStore(dict):
    """Target page store: ``id -> properties``; ``mutate`` emulates a server quirk."""

    def __init__(self, pages=None):
        super().__init__(pages or {})
        self.mutate = None


class _Context:
    def __init__(self):
        self.executions = 0

    def execute_query(self):
        self.executions += 1


class _Item:
    def __init__(self, store, page_id, fields=None):
        self.store = store
        self.page_id = page_id
        self.properties = {name: value for name, value in store[page_id].items() if fields is None or name in fields}
        self.updates: list[dict] = []

    def set_property(self, name, value):
        self.properties[name] = value

    def update(self):
        self.store[self.page_id].update(self.properties)
        self.updates.append(dict(self.properties))
        if self.store.mutate is not None:
            self.store.mutate(self.store[self.page_id])


class _Items:
    def __init__(self, store):
        self.store = store
        self.select_calls: list[tuple[str, ...]] = []
        self._fields = None

    def select(self, fields):
        self.select_calls.append(tuple(fields))
        self._fields = tuple(fields)
        return self

    def get(self):
        return self

    def execute_query(self):
        return [_Item(self.store, page_id, self._fields) for page_id in sorted(self.store)]


class _PageList:
    def __init__(self, title, store, base_template=PAGE_LIBRARY_TEMPLATE, hidden=False):
        self.title = title
        self.base_template = base_template
        self.hidden = hidden
        self.store = store
        self.items = _Items(store)

    def get_item_by_id(self, item_id):
        return _Item(self.store, item_id)


class _Lists:
    def __init__(self, lists):
        self._lists = list(lists)

    def get(self):
        return self

    def execute_query(self):
        return list(self._lists)


class _Created:
    def __init__(self, properties):
        self.properties = properties


class _PageHandle:
    def __init__(self, web, page_id):
        self.web = web
        self.page_id = page_id

    def publish(self):
        self.web.published.append(self.page_id)
        self.web.store[self.page_id]["OData__ModerationStatus"] = 0
        return self

    def execute_query(self):
        return self.web.context.execute_query()


class _Web:
    def __init__(self, *lists, store=None):
        self._lists = list(lists)
        self.lists = _Lists(self._lists)
        self.context = _Context()
        self.store = store if store is not None else _PageStore()
        self.published: list[int] = []
        self.fail_create: set[str] = set()

    def add_site_page(self, name, title=None):
        if name in self.fail_create:
            raise RuntimeError(f"cannot create {name}")
        page_id = max(self.store) + 1 if self.store else 1
        self.store[page_id] = {
            "Id": page_id,
            "FileLeafRef": name,
            "Title": title or name,
            "CanvasContent1": "",
            "OData__ModerationStatus": 3,
        }
        return _Created({"Id": page_id, "FileLeafRef": name})

    def get_site_page_by_id(self, page_id):
        return _PageHandle(self, page_id)


def _source_web(*pages):
    store = _PageStore({index: dict(page) for index, page in enumerate(pages, start=1)})
    return _Web(_PageList("Site Pages", store), store=store)


def _target_web(*pages):
    store = _PageStore({index: dict(page) for index, page in enumerate(pages, start=1)})
    return _Web(_PageList("Site Pages", store), store=store)


def _page_props(name, canvas="<div>hi</div>", content_type=_SITE_PAGE_CONTENT_TYPE, status=0, **extra):
    properties = {
        "Id": 1,
        "FileLeafRef": name,
        "Title": name.rsplit(".", 1)[0],
        "ContentTypeId": content_type,
        "CanvasContent1": canvas,
        "OData__ModerationStatus": status,
    }
    properties.update(extra)
    return properties


class TestIsModernPage(unittest.TestCase):
    def test_content_type_prefix_marks_a_modern_page(self):
        self.assertTrue(is_modern_page(_SITE_PAGE_CONTENT_TYPE, None))

    def test_canvas_marks_a_modern_page_even_without_a_known_content_type(self):
        self.assertTrue(is_modern_page(None, "<div></div>"))

    def test_wiki_page_is_not_modern(self):
        self.assertFalse(is_modern_page(_WIKI_CONTENT_TYPE, None))


class TestCaptureSitePages(unittest.TestCase):
    def test_reads_modern_pages_and_skips_classic_ones(self):
        web = _source_web(
            _page_props("Home.aspx", canvas=_WEB_PART_CONTROL),
            _page_props("Guide.aspx", canvas=None, content_type=_WIKI_CONTENT_TYPE),
        )

        payloads = capture_site_pages(web._lists[0])

        self.assertEqual([page.name for page in payloads], ["Home.aspx"])
        self.assertEqual(payloads[0].web_parts, 1)

    def test_ignores_non_aspx_items(self):
        web = _source_web(_page_props("data.json"))

        self.assertEqual(capture_site_pages(web._lists[0]), [])


class TestApplyPagePayload(unittest.TestCase):
    def test_writes_only_the_values_the_source_carries(self):
        store = _PageStore({1: {"Id": 1, "FileLeafRef": "A.aspx"}})
        item = _Item(store, 1)

        apply_page_payload(item, PagePayload(name="A.aspx", canvas="<div>x</div>", title="A"))

        self.assertEqual(item.properties["CanvasContent1"], "<div>x</div>")
        self.assertEqual(item.properties["Title"], "A")
        self.assertNotIn("Description", item.properties)
        self.assertEqual(len(item.updates), 1)

    def test_skips_none_values_entirely(self):
        store = _PageStore({1: {"Id": 1, "FileLeafRef": "A.aspx", "LayoutWebpartsContent": "keep"}})
        item = _Item(store, 1)

        apply_page_payload(item, PagePayload(name="A.aspx", canvas="<div>x</div>"))

        self.assertEqual(item.properties["LayoutWebpartsContent"], "keep")


class TestCopySitePages(unittest.TestCase):
    def test_copies_a_modern_page_and_publishes_it(self):
        source = _source_web(_page_props("Home.aspx", canvas="<div>home</div>"))
        target = _target_web()

        report = copy_site_pages(source, target, duplicate_behavior=DUPLICATE_RENAME)

        self.assertEqual(report.copied, ["Home.aspx"])
        self.assertEqual(report.published, ["Home.aspx"])
        self.assertEqual(len(target.published), 1)
        stored = next(iter(target.store.values()))
        self.assertEqual(stored["CanvasContent1"], "<div>home</div>")
        self.assertEqual(stored["OData__ModerationStatus"], 0)
        self.assertEqual(report.mismatched, [])
        self.assertEqual(report.summary(), "page copy: 1 page(s) copied, 1 published")
        # The verify read finds an identical canvas.
        self.assertEqual(verify_page_copy(source, target), [])

    def test_classic_pages_are_reported_not_copied(self):
        source = _source_web(_page_props("Guide.aspx", canvas=None, content_type=_WIKI_CONTENT_TYPE))
        target = _target_web()

        report = copy_site_pages(source, target)

        self.assertEqual(report.classic, ["Guide.aspx"])
        self.assertTrue(report.is_empty)
        self.assertIsNone(report.summary())
        self.assertEqual(target.store, {})
        note = page_handoff_note(detect_page_handoff(source._lists), modern_copied=True)
        self.assertIn("classic page(s) are not migrated", note)
        self.assertIn("Guide.aspx", note)

    def test_duplicate_page_is_renamed_by_default(self):
        source = _source_web(_page_props("Home.aspx", canvas="<div>source</div>"))
        target = _target_web()
        target.store[1] = {"Id": 1, "FileLeafRef": "Home.aspx", "CanvasContent1": "<div>target</div>"}

        report = copy_site_pages(source, target)

        self.assertEqual(report.copied, ["Home-1.aspx"])
        self.assertEqual(report.renamed, [("Home.aspx", "Home-1.aspx")])
        self.assertEqual(target.store[1]["CanvasContent1"], "<div>target</div>")
        self.assertIn("1 renamed around an existing page", report.summary())

    def test_rename_skips_names_that_are_already_taken(self):
        source = _source_web(_page_props("Home.aspx"))
        target = _target_web()
        target.store[1] = {"Id": 1, "FileLeafRef": "Home.aspx"}
        target.store[2] = {"Id": 2, "FileLeafRef": "Home-1.aspx"}

        report = copy_site_pages(source, target)

        self.assertEqual(report.copied, ["Home-2.aspx"])

    def test_duplicate_page_can_be_skipped(self):
        source = _source_web(_page_props("Home.aspx", canvas="<div>source</div>"))
        target = _target_web()
        target.store[1] = {"Id": 1, "FileLeafRef": "Home.aspx", "CanvasContent1": "<div>target</div>"}

        report = copy_site_pages(source, target, duplicate_behavior=DUPLICATE_SKIP)

        self.assertEqual(report.skipped, ["Home.aspx"])
        self.assertEqual(report.copied, [])
        self.assertEqual(target.store[1]["CanvasContent1"], "<div>target</div>")
        self.assertIn("1 left as they were", report.summary())

    def test_duplicate_page_can_be_overwritten_in_place(self):
        source = _source_web(_page_props("Home.aspx", canvas="<div>source</div>"))
        target = _target_web()
        target.store[1] = {"Id": 1, "FileLeafRef": "Home.aspx", "CanvasContent1": "<div>target</div>"}

        report = copy_site_pages(source, target, duplicate_behavior=DUPLICATE_OVERWRITE)

        self.assertEqual(report.overwritten, ["Home.aspx"])
        self.assertEqual(report.copied, [])
        self.assertEqual(target.store[1]["CanvasContent1"], "<div>source</div>")
        self.assertEqual(len(target.store), 1)

    def test_unknown_duplicate_behavior_falls_back_to_rename(self):
        source = _source_web(_page_props("Home.aspx"))
        target = _target_web()
        target.store[1] = {"Id": 1, "FileLeafRef": "Home.aspx"}
        warnings: list[str] = []

        report = copy_site_pages(source, target, duplicate_behavior="MOVE", warnings=warnings)

        self.assertEqual(report.copied, ["Home-1.aspx"])
        self.assertTrue(any("unknown duplicate behavior" in note for note in warnings))

    def test_a_draft_page_is_copied_without_publishing(self):
        source = _source_web(_page_props("Draft.aspx", status=3))
        target = _target_web()

        report = copy_site_pages(source, target)

        self.assertEqual(report.copied, ["Draft.aspx"])
        self.assertEqual(report.published, [])
        self.assertEqual(target.published, [])
        self.assertEqual(report.summary(), "page copy: 1 page(s) copied")

    def test_one_failing_page_does_not_abort_the_others(self):
        source = _source_web(_page_props("A.aspx"), _page_props("B.aspx"))
        target = _target_web()
        target.fail_create = {"B.aspx"}
        warnings: list[str] = []

        report = copy_site_pages(source, target, warnings=warnings)

        self.assertEqual(report.copied, ["A.aspx"])
        self.assertEqual(len(report.failed), 1)
        self.assertEqual(report.failed[0][0], "B.aspx")
        self.assertTrue(any("could not be copied" in note for note in warnings))

    def test_a_canvas_that_does_not_read_back_is_reported(self):
        source = _source_web(_page_props("Home.aspx", canvas="<div>source</div>"))
        target = _target_web()
        target.store.mutate = lambda properties: properties.pop("CanvasContent1", None)
        warnings: list[str] = []

        report = copy_site_pages(source, target, warnings=warnings)

        self.assertEqual(report.copied, ["Home.aspx"])
        self.assertEqual(report.mismatched, ["Home.aspx"])
        self.assertTrue(any("did not read back their canvas" in note for note in warnings))

    def test_web_part_pages_are_reported(self):
        source = _source_web(_page_props("News.aspx", canvas=_WEB_PART_CONTROL))
        target = _target_web()
        warnings: list[str] = []

        report = copy_site_pages(source, target, warnings=warnings)

        self.assertEqual(report.web_part_pages, ["News.aspx"])
        self.assertTrue(any("client-side web parts" in note for note in warnings))

    def test_a_source_without_page_libraries_does_nothing(self):
        source = _Web(_PageList("Documents", _PageStore(), base_template=101))
        target = _target_web()

        report = copy_site_pages(source, target)

        self.assertTrue(report.is_empty)
        self.assertEqual(report.libraries, [])

    def test_a_target_without_a_page_library_is_reported(self):
        source = _source_web(_page_props("Home.aspx"))
        target = _Web(_PageList("Documents", _PageStore(), base_template=101))
        warnings: list[str] = []

        report = copy_site_pages(source, target, warnings=warnings)

        self.assertTrue(report.is_empty)
        self.assertEqual(report.classic, [])
        self.assertTrue(any("no target page library matches" in note for note in warnings))

    def test_a_renamed_copy_is_not_reported_as_drift(self):
        source = _source_web(_page_props("Home.aspx", canvas="<div>same</div>"))
        target = _target_web()
        target.store[1] = {"Id": 1, "FileLeafRef": "Home.aspx", "CanvasContent1": "<div>other</div>"}

        report = copy_site_pages(source, target)

        self.assertEqual(report.copied, ["Home-1.aspx"])
        # The renamed copy carries the source canvas; the same-named target page
        # drifted by design (it was not ours to overwrite).
        self.assertEqual(verify_page_copy(source, target), ["1 page(s) differ from the source: Home.aspx"])


class TestVerifyPageCopy(unittest.TestCase):
    def test_missing_page_is_named(self):
        source = _source_web(_page_props("Home.aspx", canvas="<div>source</div>"))
        target = _target_web()

        notes = verify_page_copy(source, target)

        self.assertEqual(notes, ["1 modern page(s) have no target counterpart: Home.aspx"])

    def test_matching_page_is_quiet(self):
        source = _source_web(_page_props("Home.aspx", canvas="<div>same</div>"))
        target = _target_web({"Id": 1, "FileLeafRef": "Home.aspx", "CanvasContent1": "<div>same</div>"})

        self.assertEqual(verify_page_copy(source, target), [])

    def test_source_without_pages_is_quiet(self):
        self.assertEqual(verify_page_copy(_source_web(), _target_web()), [])


if __name__ == "__main__":
    unittest.main()
