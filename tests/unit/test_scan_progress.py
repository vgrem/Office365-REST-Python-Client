"""Offline tests for progress hooks on recursive scan operations (get_files/get_folders/get_all_webs)."""

from __future__ import annotations

import json as jsonlib
import unittest

from office365.runtime.transport.base import BaseTransport
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.navigation.nodes.collection import NavigationNodeCollection
from requests import Response

_METADATA = {"__metadata": {"type": "SP.Folder"}}


def _files_result(urls: list[str]) -> dict:
    return {"d": {"results": [{"__metadata": {"type": "SP.File"}, "ServerRelativeUrl": u} for u in urls]}}


def _folders_result(urls: list[str]) -> dict:
    return {"d": {"results": [{**_METADATA, "ServerRelativeUrl": u} for u in urls]}}


class _ScriptedTransport(BaseTransport):
    def __init__(self, payloads: list[dict]) -> None:
        self._payloads = payloads
        self.calls = 0

    def execute(self, request):
        payload = self._payloads[min(self.calls, len(self._payloads) - 1)]
        self.calls += 1
        resp = Response()
        resp.status_code = 200
        resp.url = request.url
        resp.headers.update({"Content-Type": "application/json;odata=verbose"})
        resp._content = jsonlib.dumps(payload).encode("utf-8")
        return resp


class TestScanProgress(unittest.TestCase):
    def _context(self, transport: _ScriptedTransport) -> ClientContext:
        ctx = ClientContext("https://contoso.sharepoint.com/sites/x")
        ctx.pending_request().beforeExecute.clear()  # no auth handler during offline build
        ctx.pending_request().transport = transport
        return ctx

    def test_get_files_recursive_fires_per_folder(self):
        payloads = [
            _files_result(["/a.txt", "/b.txt"]),  # root folder's files
            _folders_result(["/sub"]),  # root folder's sub-folders
            _files_result(["/sub/c.txt"]),  # the sub-folder's files
            _folders_result([]),  # the sub-folder has no further sub-folders
        ]
        ctx = self._context(_ScriptedTransport(payloads))
        seen = []
        folder = ctx.web.get_folder_by_server_relative_url("Shared Documents")

        folder.get_files(True, progress=seen.append).execute_query()

        # root scan then the sub-folder scan, with cumulative done
        self.assertEqual([p.done for p in seen], [2, 3])  # noqa: PLR2004
        self.assertEqual([f.server_relative_url for f in (seen[-1].items or [])], ["/sub/c.txt"])


def _nav_node(node_id: int, title: str, url: str) -> dict:
    return {"__metadata": {"type": "SP.NavigationNode"}, "Id": node_id, "Title": title, "Url": url}


class TestNavigationGetAll(unittest.TestCase):
    _PAYLOADS = [
        {"d": {"results": [_nav_node(1, "Home", "/"), _nav_node(2, "About", "/about")]}},
        {"d": {"results": []}},  # Home.children
        {"d": {"results": [_nav_node(3, "Team", "/about/team")]}},  # About.children
        {"d": {"results": []}},  # Team.children
    ]

    def _walk(self, progress=None) -> tuple[NavigationNodeCollection, list]:
        ctx = ClientContext("https://contoso.sharepoint.com/sites/x")
        ctx.pending_request().beforeExecute.clear()
        ctx.pending_request().transport = _ScriptedTransport(self._PAYLOADS)
        seen = []
        hook = progress or seen.append
        nodes = ctx.web.navigation.top_navigation_bar.get_all_nodes(recursive=True, progress=hook).execute_query()
        return nodes, seen

    def test_get_all_walks_all_nodes(self):
        nodes, seen = self._walk()
        self.assertEqual([n.get_property("Title") for n in nodes], ["Home", "About", "Team"])
        self.assertEqual([p.done for p in seen], [1, 2, 3])  # noqa: PLR2004


if __name__ == "__main__":
    unittest.main()
