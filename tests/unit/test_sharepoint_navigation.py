"""Offline tests for best-effort web navigation replication.

The item adapters carry content; ``navigation.py`` copies a web's Quick Launch and
top navigation bar. These tests drive it with fakes — no network — and assert that
missing nodes are created with rewritten links, existing nodes are reconciled
rather than duplicated, URL-less (dynamic) nodes are skipped with a warning, and a
web that inherits its navigation only flips the target's ``use_shared`` flag.
"""

from __future__ import annotations

from office365.migration.sharepoint.navigation import (
    apply_navigation,
    capture_navigation,
    verify_navigation,
)


class _Nodes:
    def __init__(self, items=()) -> None:
        self._items = list(items)

    def get(self):
        return self

    def execute_query(self):
        return list(self._items)

    def add(self, info):
        node = _Node(title=info.Title, url=info.Url, is_external=info.IsExternal)
        self._items.append(node)
        return node


class _Node:
    def __init__(self, title: str, url: str, is_external: bool = False, is_visible: bool = True, children=()) -> None:
        self.title = title
        self.url = url
        self.is_external = is_external
        self.is_visible = is_visible
        self.children = _Nodes(children)

    def execute_query(self):
        return self


class _Navigation:
    def __init__(self, use_shared: bool = False, quick_launch=(), top=()) -> None:
        self.use_shared = use_shared
        self.quick_launch = _Nodes(quick_launch)
        self.top_navigation_bar = _Nodes(top)
        self.updates = 0

    def get(self):
        return self

    def execute_query(self):
        return self

    def update(self):
        self.updates += 1
        return self


class _Web:
    def __init__(self, url: str, navigation: _Navigation) -> None:
        self.url = url
        self.navigation = navigation
        self.executed = 0
        self.context = self

    def execute_query(self):
        self.executed += 1


def _source_web():
    custom = _Node("Wiki", "/sites/team_in/Pages/Wiki.aspx", children=[_Node("Sub", "https://intranet.example.com")])
    recent = _Node("Recent", "", children=[_Node("Depts", "/sites/team_in/Lists/Depts/AllItems.aspx")])
    quick_launch = [
        _Node("Home", "/sites/team_in"),
        recent,
        _Node("Recent-ish", "/sites/team_in/Shared Documents"),
        custom,
    ]
    return _Web("https://mediadev8.sharepoint.com/sites/team_in", _Navigation(quick_launch=quick_launch))


def _target_web(*, with_wiki: bool = False):
    quick_launch = [_Node("Home", "/sites/team_out"), _Node("Recent", "")]
    if with_wiki:
        quick_launch.append(_Node("Wiki", "/sites/team_out/Pages/Wiki.aspx"))
    navigation = _Navigation(quick_launch=quick_launch)
    return _Web("https://mediadev8.sharepoint.com/sites/team_out", navigation)


def test_capture_reads_both_bars_and_skips_children_of_url_less_nodes():
    source = _source_web()

    captured = capture_navigation(source)

    assert [n.title for n in captured.quick_launch] == ["Home", "Recent", "Recent-ish", "Wiki"]
    recent = captured.quick_launch[1]
    assert recent.url == ""
    assert recent.children == []  # the dynamic node's computed children are not read
    wiki = captured.quick_launch[3]
    assert [c.title for c in wiki.children] == ["Sub"]


def test_apply_creates_missing_nodes_with_rewritten_links():
    source, target = _source_web(), _target_web()

    warnings: list[str] = []
    apply_navigation(source, target, warnings)

    created = {n.title: n for n in target.navigation.quick_launch.execute_query()}
    assert created["Wiki"].url == "/sites/team_out/Pages/Wiki.aspx"
    assert [c.title for c in created["Wiki"].children.execute_query()] == ["Sub"]
    assert created["Wiki"].children.execute_query()[0].url == "https://intranet.example.com"
    # the dynamic node is skipped and reported, never created
    assert "Recent" in created and created["Recent"].url == ""
    assert any("Recent" in w and "no URL" in w for w in warnings)
    # Home already existed by title, so it is neither re-created nor rewritten
    assert created["Home"].url == "/sites/team_out"
    assert target.executed == 1


def test_verify_reports_missing_and_mismatched_nodes_and_is_clean_when_replicated():
    source, target = _source_web(), _target_web()

    issues = verify_navigation(source, target)
    assert any("Wiki" in i and "not created" in i for i in issues)

    apply_navigation(source, target, [])
    assert verify_navigation(source, target) == []

    target.navigation.quick_launch.execute_query()[0].url = "/sites/team_out/Elsewhere"
    assert any("Home" in i and "expected" in i for i in verify_navigation(source, target))
