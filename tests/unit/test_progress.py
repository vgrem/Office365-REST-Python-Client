"""Offline tests for the optional tqdm-backed progress hook."""

import json as jsonlib
import sys
import types
import unittest

from office365.runtime.operations import Progress
from office365.runtime.progress import progress_bar
from office365.runtime.transport.base import BaseTransport
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.navigation.nodes.collection import NavigationNodeCollection
from requests import Response

_TOTAL = 10
_FIRST_DONE = 3
_SECOND_DONE = 10
_ADOPTED_TOTAL = 12


class _FakeBar:
    """Minimal stand-in for ``tqdm.tqdm`` recording updates and closes."""

    def __init__(self, desc=None, total=None):
        self.desc = desc
        self.total = total
        self.n = 0
        self.closed = False
        self.updates: list[int] = []

    def update(self, n):
        self.n += n
        self.updates.append(n)

    def close(self):
        self.closed = True


def _install_fake_tqdm(monkeypatch) -> list[_FakeBar]:
    """Register a fake ``tqdm`` module and return every bar it creates."""
    instances: list[_FakeBar] = []

    class FakeBar(_FakeBar):
        def __init__(self, desc=None, total=None):
            super().__init__(desc=desc, total=total)
            instances.append(self)

    fake = types.ModuleType("tqdm")
    fake.tqdm = FakeBar
    monkeypatch.setitem(sys.modules, "tqdm", fake)
    return instances


def test_progress_bar_advances_a_fake_tqdm(monkeypatch):
    instances = _install_fake_tqdm(monkeypatch)

    hook = progress_bar("scan", total=_TOTAL)
    hook(Progress(done=_FIRST_DONE, total=_TOTAL))
    hook(Progress(done=_SECOND_DONE, total=_ADOPTED_TOTAL))

    bar = instances[0]
    assert bar.desc == "scan"
    assert bar.updates == [_FIRST_DONE, _SECOND_DONE - _FIRST_DONE]
    assert bar.n == _SECOND_DONE
    assert bar.total == _ADOPTED_TOTAL
    assert bar.closed is False


_METADATA = {"__metadata": {"type": "SP.Folder"}}


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
