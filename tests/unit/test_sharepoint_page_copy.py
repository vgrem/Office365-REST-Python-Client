"""Tests for the site page copy (create + fill + publish + verify), modern and classic wiki."""

import unittest

from office365.migration.sharepoint.pages import (
    DUPLICATE_RENAME,
    PAGE_LIBRARY_TEMPLATE,
    capture_site_pages,
    copy_site_pages,
    detect_page_handoff,
    page_handoff_note,
    verify_page_copy,
)

# A modern site page content type (inherited from the Site Page base content type).
_SITE_PAGE_CONTENT_TYPE = "0x0101009D1CB255DA76424F860D91F20E6C4118005E10E40F8E37D94AB983A0181120EFFC"
_WIKI_CONTENT_TYPE = "0x010108"
# A publishing page (``SP.Publishing.PublishingPage``) carries neither a canvas nor a wiki body.
_PUBLISHING_CONTENT_TYPE = "0x010100C568DB52D9D0A14D9B2FDCC96666E9F2007948130EC3DB064584E219954237AF39"

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


class _FileHandle:
    """A list item's file: only ``publish`` is used by the classic page copy."""

    def __init__(self, web, page_id):
        self.web = web
        self.page_id = page_id

    def publish(self, comment):
        self.web.published.append(self.page_id)
        self.web.store[self.page_id]["OData__ModerationStatus"] = 0
        return self

    def execute_query(self):
        return self.web.context.execute_query()


class _Item:
    def __init__(self, store, page_id, fields=None, web=None):
        self.store = store
        self.page_id = page_id
        self.web = web
        self.properties = {name: value for name, value in store[page_id].items() if fields is None or name in fields}
        self.updates: list[dict] = []

    @property
    def file(self):
        return _FileHandle(self.web, self.page_id)

    def set_property(self, name, value):
        self.properties[name] = value

    def update(self):
        self.store[self.page_id].update(self.properties)
        self.updates.append(dict(self.properties))
        if self.store.mutate is not None:
            self.store.mutate(self.store[self.page_id])


class _Items:
    def __init__(self, store, web=None):
        self.store = store
        self.web = web
        self.select_calls: list[tuple[str, ...]] = []
        self._fields = None

    def select(self, fields):
        self.select_calls.append(tuple(fields))
        self._fields = tuple(fields)
        return self

    def get(self):
        return self

    def execute_query(self):
        return [_Item(self.store, page_id, self._fields, self.web) for page_id in sorted(self.store)]


class _CreatedItemField:
    """``File.list_item_all_fields`` on a create response: a projected read of the item."""

    def __init__(self, web, page_id):
        self.web = web
        self.page_id = page_id
        self._fields = None

    def select(self, fields):
        self._fields = tuple(fields)
        return self

    def get(self):
        return self

    def execute_query(self):
        return _Item(self.web.store, self.page_id, self._fields, self.web)


class _CreatedWikiPage:
    """The ``File`` a ``create_wiki_page`` call returns."""

    def __init__(self, web, page_id):
        self.web = web
        self.page_id = page_id
        self.list_item_all_fields = _CreatedItemField(web, page_id)

    def execute_query(self):
        return self


class _PageList:
    def __init__(self, title, store, base_template=PAGE_LIBRARY_TEMPLATE, hidden=False):
        self.title = title
        self.base_template = base_template
        self.hidden = hidden
        self.store = store
        self.web = None
        self.items = _Items(store)

    def get_item_by_id(self, item_id):
        return _Item(self.store, item_id, web=self.web)

    def create_wiki_page(self, name, body):
        if name in self.web.fail_create:
            raise RuntimeError(f"cannot create {name}")
        self.web.wiki_created.append((name, body))
        page_id = max(self.store) + 1 if self.store else 1
        self.store[page_id] = {
            "Id": page_id,
            "FileLeafRef": name,
            "FileRef": f"/sites/target/SitePages/{name}",
            "WikiField": body,
            "CanvasContent1": None,
            "OData__ModerationStatus": 3,
        }
        return _CreatedWikiPage(self.web, page_id)


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


class _RootFolder:
    """``Web.root_folder``: the endpoint that actually carries a ``WelcomePage`` write."""

    def __init__(self, web):
        self.web = web
        self.written: dict = {}
        self.properties = {
            "ServerRelativeUrl": self.web.properties.get("ServerRelativeUrl", "/sites/target"),
            "WelcomePage": self.web.properties.get("WelcomePage"),
        }

    def select(self, fields):
        return self

    def get(self):
        return self

    def execute_query(self):
        return self

    def set_property(self, name, value):
        self.written[name] = value

    def update(self):
        self.web.properties["WelcomePage"] = self.written.get("WelcomePage")
        return self


class _Web:
    def __init__(self, *lists, store=None, welcome_page=None):
        self._lists = list(lists)
        self.lists = _Lists(self._lists)
        self.context = _Context()
        self.store = store if store is not None else _PageStore()
        self.published: list[int] = []
        self.wiki_created: list[tuple[str, str]] = []
        self.fail_create: set[str] = set()
        self.properties = {"ServerRelativeUrl": "/sites/target", "WelcomePage": welcome_page}
        self.root_folder = _RootFolder(self)
        for sp_list in self._lists:
            sp_list.web = self

    def select(self, fields):
        return self

    def get(self):
        return self

    def execute_query(self):
        return self

    def add_site_page(self, name, title=None):
        if name in self.fail_create:
            raise RuntimeError(f"cannot create {name}")
        page_id = max(self.store) + 1 if self.store else 1
        self.store[page_id] = {
            "Id": page_id,
            "FileLeafRef": name,
            "FileRef": f"/sites/target/SitePages/{name}",
            "Title": title or name,
            "CanvasContent1": "",
            "OData__ModerationStatus": 3,
        }
        return _Created({"Id": page_id, "FileLeafRef": name})

    def get_site_page_by_id(self, page_id):
        return _PageHandle(self, page_id)


def _source_web(*pages, welcome_page=None):
    store = _PageStore({index: dict(page) for index, page in enumerate(pages, start=1)})
    return _Web(_PageList("Site Pages", store), store=store, welcome_page=welcome_page)


def _target_web(*pages, welcome_page=None):
    store = _PageStore({index: dict(page) for index, page in enumerate(pages, start=1)})
    return _Web(_PageList("Site Pages", store), store=store, welcome_page=welcome_page)


def _wiki_page_props(name, body, status=0):
    return _page_props(name, canvas=None, content_type=_WIKI_CONTENT_TYPE, status=status, WikiField=body)


def _page_props(name, canvas="<div>hi</div>", content_type=_SITE_PAGE_CONTENT_TYPE, status=0, **extra):
    properties = {
        "Id": 1,
        "FileLeafRef": name,
        "FileRef": f"/sites/target/SitePages/{name}",
        "Title": name.rsplit(".", 1)[0],
        "ContentTypeId": content_type,
        "CanvasContent1": canvas,
        "OData__ModerationStatus": status,
    }
    properties.update(extra)
    return properties


class TestCaptureSitePages(unittest.TestCase):
    def test_reads_modern_and_classic_pages(self):
        web = _source_web(
            _page_props("Home.aspx", canvas=_WEB_PART_CONTROL),
            _wiki_page_props("Guide.aspx", "<p>wiki</p>"),
            _page_props("Blank.aspx", canvas=None, content_type=_PUBLISHING_CONTENT_TYPE),
        )

        payloads = capture_site_pages(web._lists[0])

        self.assertEqual([page.name for page in payloads], ["Home.aspx", "Guide.aspx"])
        self.assertEqual(payloads[0].web_parts, 1)
        self.assertTrue(payloads[1].is_classic)
        self.assertEqual(payloads[1].content, "<p>wiki</p>")
        self.assertEqual(payloads[1].to_dict()["wiki_length"], len("<p>wiki</p>"))


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

    def test_a_classic_wiki_page_is_copied_through_its_wiki_field(self):
        source = _source_web(_wiki_page_props("Guide.aspx", "<p>classic</p>"))
        target = _target_web()
        warnings: list[str] = []

        report = copy_site_pages(source, target, warnings=warnings)

        self.assertEqual(report.copied, ["Guide.aspx"])
        self.assertEqual(report.wiki, ["Guide.aspx"])
        self.assertEqual(target.wiki_created, [("Guide.aspx", "<p>classic</p>")])
        stored = next(iter(target.store.values()))
        self.assertEqual(stored["WikiField"], "<p>classic</p>")
        self.assertIsNone(stored["CanvasContent1"])
        # A created wiki page is a draft, so the copy publishes it as the source was.
        self.assertEqual(report.published, ["Guide.aspx"])
        self.assertEqual(len(target.published), 1)
        self.assertEqual(report.mismatched, [])
        self.assertEqual(report.summary(), "page copy: 1 page(s) copied (1 classic wiki), 1 published")
        self.assertTrue(any("copied verbatim" in note for note in warnings))
        self.assertEqual(verify_page_copy(source, target), [])
        self.assertIsNone(page_handoff_note(detect_page_handoff(source._lists), modern_copied=True))

    def test_a_second_run_finds_its_own_renamed_copy_and_leaves_it_alone(self):
        source = _source_web(_page_props("Home.aspx", canvas="<div>source</div>"))
        target = _target_web(_page_props("Home.aspx", canvas="<div>target</div>"))

        first = copy_site_pages(source, target)
        second = copy_site_pages(source, target)

        self.assertEqual(first.copied, ["Home-1.aspx"])
        self.assertEqual(first.renamed, [("Home.aspx", "Home-1.aspx")])
        # The body is the copy's identity, so the re-run recognizes the page it made.
        self.assertEqual(second.copied, [])
        self.assertEqual(second.unchanged, ["Home.aspx"])
        self.assertEqual(second.renamed, [("Home.aspx", "Home-1.aspx")])
        self.assertEqual(len(target.store), 2)
        self.assertEqual(second.summary(), "page copy: 1 already copied")
        self.assertEqual(verify_page_copy(source, target), [])

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


class TestHomePage(unittest.TestCase):
    """A migrated site must open on the copy of the source's home page."""

    def test_the_home_page_follows_the_copy(self):
        source = _source_web(_page_props("Home.aspx"), welcome_page="SitePages/Home.aspx")
        target = _target_web()

        report = copy_site_pages(source, target)

        self.assertEqual(report.home_page, "SitePages/Home.aspx")
        self.assertEqual(target.properties["WelcomePage"], "SitePages/Home.aspx")
        self.assertEqual(target.root_folder.written, {"WelcomePage": "SitePages/Home.aspx"})
        self.assertIn("home page is now SitePages/Home.aspx", report.summary())


if __name__ == "__main__":
    unittest.main()
