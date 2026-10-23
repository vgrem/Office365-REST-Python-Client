"""Merged unit tests (consolidated; see git history for originals)."""

from __future__ import annotations

import json as jsonlib
import unittest
from types import SimpleNamespace

from office365.directory.users.user import User
from office365.graph_client import GraphClient
from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.transport.base import BaseTransport
from office365.sharepoint.client_context import ClientContext
from requests import Response
from tests import test_site_url
from tests._scripted_transport import ScriptedTransport as _ScriptedTransport

NEXT_LINK = "https://graph.microsoft.com/v1.0/users?$skiptoken=abc"

PAGE_1_HEADERS = {
    "Authorization": "Bearer real",
    "ConsistencyLevel": "eventual",
    "X-Custom": "1",
    "Content-Length": "42",
}


class _FakeTransport(BaseTransport):
    def __init__(self) -> None:
        self.requests: list = []

    def execute(self, request):
        self.requests.append(request)
        resp = Response()
        resp.status_code = 200
        resp.url = request.url
        resp.headers.update({"Content-Type": "application/json"})
        resp._content = jsonlib.dumps({"@odata.nextLink": NEXT_LINK, "value": []}).encode("utf-8")
        resp.request = SimpleNamespace(headers=dict(PAGE_1_HEADERS))  # type: ignore[assignment]
        return resp


def _page1(col: ClientObjectCollection) -> _FakeTransport:
    client = col.context
    client.pending_request().beforeExecute.clear()  # no auth handler during offline build
    transport = _FakeTransport()
    client.pending_request().transport = transport
    col.paged(10).get().execute_query()
    return transport


class TestPagingHeaders(unittest.TestCase):
    def test_next_page_reapplies_custom_headers(self):
        client = GraphClient()
        col = ClientObjectCollection(client, User, ResourcePath("users"))
        transport = _page1(col)

        col._get_next()
        col.execute_query()

        request = transport.requests[-1]
        self.assertEqual(request.url, NEXT_LINK)
        self.assertEqual(request.headers.get("ConsistencyLevel"), "eventual")
        self.assertEqual(request.headers.get("X-Custom"), "1")


def _page(items: list) -> dict:
    return {"d": {"results": [{"Id": str(i), "Title": f"List {i}"} for i in items]}}


class _CaptureTransport(_ScriptedTransport):
    def __init__(self, payloads):
        super().__init__(payloads)
        self.urls: list[str] = []
        self.bodies: list = []

    def execute(self, request):
        self.urls.append(request.url)
        self.bodies.append(request.data)
        return super().execute(request)


def _file_page(names: list[str]) -> dict:
    return {"d": {"results": [{"Name": n, "ServerRelativeUrl": f"/Shared Documents/{n}"} for n in names]}}


def _caml_items_page(ids: list[int], next_url: str | None = None) -> dict:
    page: dict = {"results": [{"Id": i, "Title": f"Item {i}"} for i in ids]}
    if next_url:
        page["__next"] = next_url
    return {"d": page}


class TestLargeCollectionPaging(unittest.TestCase):
    """Folder.get_files and List.get_items page instead of throttling on large collections."""

    def _context(self, payloads: list) -> tuple[ClientContext, _CaptureTransport]:
        ctx = ClientContext(test_site_url)
        transport = _CaptureTransport(payloads)
        ctx.pending_request().beforeExecute.clear()
        ctx.pending_request().transport = transport
        return ctx, transport

    def test_folder_get_files_pages(self):
        ctx, transport = self._context([_file_page(["a.txt", "b.txt"]), _file_page(["c.txt", "d.txt"]), _file_page([])])
        folder = ctx.web.get_folder_by_server_relative_url("/Shared Documents/big")

        files = folder.get_files(page_size=2).execute_query()

        self.assertEqual([f.properties.get("Name") for f in files], ["a.txt", "b.txt", "c.txt", "d.txt"])
        self.assertEqual(transport.calls, 3)  # noqa: PLR2004

    def test_list_get_items_pages_with_page_size(self):
        ctx, transport = self._context([_caml_items_page([1, 2]), _caml_items_page([3, 4]), _caml_items_page([])])

        items = ctx.web.lists.get_by_title("X").get_items(page_size=2).execute_query()

        self.assertEqual([i.properties.get("Id") for i in items], [1, 2, 3, 4])
        # the next GetItems call continues from the last item via its position
        self.assertIn("Paged=TRUE&p_ID=2", jsonlib.dumps(transport.bodies[1]))


class TestSPOffsetPaging(unittest.TestCase):
    """When a SharePoint endpoint returns no __next link, paged(page_size) falls back to $skip."""

    def _context(self, payloads: list) -> tuple[ClientContext, _CaptureTransport]:
        ctx = ClientContext(test_site_url)
        transport = _CaptureTransport(payloads)
        ctx.pending_request().beforeExecute.clear()
        ctx.pending_request().transport = transport
        return ctx, transport

    def test_paged_falls_back_to_skip_paging(self):
        ctx, transport = self._context([_page([1, 2]), _page([3, 4]), _page([])])
        pages = ctx.web.lists.paged(2).get().execute_query()

        items = list(pages)

        self.assertEqual(len(items), 4)  # noqa: PLR2004
        self.assertEqual(transport.calls, 3)  # noqa: PLR2004
        self.assertIn("skip=2", transport.urls[1])
        self.assertIn("skip=4", transport.urls[2])

    def test_paged_stops_on_short_page(self):
        ctx, transport = self._context([_page([1, 2]), _page([3])])
        pages = ctx.web.lists.paged(2).get().execute_query()

        items = list(pages)

        self.assertEqual(len(items), 3)  # noqa: PLR2004
        self.assertEqual(transport.calls, 2)  # noqa: PLR2004
        self.assertIn("skip=2", transport.urls[1])

    def test_full_final_page_issues_one_empty_request(self):
        ctx, transport = self._context([_page([1, 2]), _page([3, 4]), _page([])])
        pages = ctx.web.lists.paged(2).get().execute_query()

        self.assertEqual(len(pages), 2)  # noqa: PLR2004
        self.assertTrue(pages.has_next)

        items = list(pages)

        self.assertEqual(len(items), 4)  # noqa: PLR2004
        self.assertEqual(transport.calls, 3)  # noqa: PLR2004


class TestServerPagedReset(unittest.TestCase):
    """A completed server-paged run must not disable $skip for a fresh enumeration."""

    def _collection(self) -> ClientObjectCollection:
        return ClientObjectCollection(GraphClient(), User, ResourcePath("users"))


class TestDedupePaging(unittest.TestCase):
    """Opt-in de-duplication by a property (Graph can repeat rows across pages)."""

    def _graph_context(self, payloads: list) -> tuple[GraphClient, _ScriptedTransport]:
        ctx = GraphClient()
        ctx.pending_request().beforeExecute.clear()
        transport = _ScriptedTransport(payloads)
        ctx.pending_request().transport = transport
        return ctx, transport

    def test_get_all_dedupes_by_id(self):
        next_1 = "https://graph.microsoft.com/v1.0/users?$skiptoken=a"
        next_2 = "https://graph.microsoft.com/v1.0/users?$skiptoken=b"
        ctx, transport = self._graph_context(
            [
                {"@odata.nextLink": next_1, "value": [{"id": "1"}, {"id": "2"}]},
                {"@odata.nextLink": next_2, "value": [{"id": "2"}, {"id": "3"}]},
                {"value": [{"id": "3"}, {"id": "4"}]},
            ]
        )

        col = ctx.users
        col.get_all(page_size=2, dedupe_by="id").execute_query()

        self.assertEqual([u.properties.get("id") for u in col], ["1", "2", "3", "4"])
        self.assertEqual(transport.calls, 3)  # noqa: PLR2004
