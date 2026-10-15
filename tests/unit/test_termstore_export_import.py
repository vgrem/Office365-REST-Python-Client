"""Tests for the term-store hierarchy export/import API.

``to_json`` / ``from_json`` are reserved for wire-payload (de)serialization, so
the term-store *hierarchy* uses the symmetric ``export_tree()`` / ``import_tree()``
on ``Store`` and ``StoreManager``. The legacy names remain as deprecated aliases,
and ``Store`` must never shadow the payload ``to_json``.
"""

from __future__ import annotations

import pytest
from office365.onedrive.termstore.store import Store
from office365.onedrive.termstore.store_manager import StoreManager
from office365.runtime.client_object import ClientObject

# ---------------------------------------------------------------------------
# Fakes: deferred collections whose ``after_execute`` fires immediately.
# ---------------------------------------------------------------------------


class _FakeTerms:
    def __init__(self, items=None):
        self.items = list(items or [])

    def get(self):
        return self

    def after_execute(self, callback):
        callback(self.items)
        return self

    def ensure(self, name):
        node = _FakeTerm(name)
        self.items.append(node)
        return node


class _FakeTerm:
    def __init__(self, name, children=None):
        self.display_name = name
        self.children = children or _FakeTerms()


class _FakeSets:
    def __init__(self, items=None):
        self.items = list(items or [])

    def get(self):
        return self

    def after_execute(self, callback):
        callback(self.items)
        return self

    def ensure(self, name):
        node = _FakeSet(name)
        self.items.append(node)
        return node


class _FakeSet:
    def __init__(self, name, children=None):
        self.display_name = name
        self.children = children or _FakeTerms()


class _FakeGroups:
    def __init__(self, items=None):
        self.items = list(items or [])

    def get(self):
        return self

    def after_execute(self, callback):
        callback(self.items)
        return self

    def ensure(self, name):
        node = _FakeGroup(name)
        self.items.append(node)
        return node


class _FakeGroup:
    def __init__(self, name, sets=None):
        self.display_name = name
        self.sets = sets or _FakeSets()

    def ensure_set(self, name):
        return self.sets.ensure(name)


EXPECTED_TREE = [
    {
        "name": "G",
        "sets": [
            {
                "name": "S",
                "children": [{"name": "T", "children": [{"name": "T2", "children": []}]}],
            }
        ],
    }
]


def _store_with(groups):
    store = Store(object())
    store._properties["groups"] = groups
    return store


def _sample_tree():
    """Group G -> set S -> term T -> child T2."""
    term = _FakeTerm("T", _FakeTerms([_FakeTerm("T2")]))
    term_set = _FakeSet("S", _FakeTerms([term]))
    group = _FakeGroup("G", _FakeSets([term_set]))
    return _FakeGroups([group])


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------


def test_store_manager_export_tree_builds_nested_tree():
    manager = StoreManager(_store_with(_sample_tree()))

    assert manager.export_tree().value == EXPECTED_TREE


def test_store_export_tree_delegates_to_manager():
    store = _store_with(_sample_tree())

    assert store.export_tree().value == EXPECTED_TREE


# ---------------------------------------------------------------------------
# Import
# ---------------------------------------------------------------------------


def test_store_import_tree_creates_queued_nodes():
    store = _store_with(_FakeGroups())
    data = [{"name": "G", "sets": [{"name": "S", "children": [{"name": "T"}]}]}]

    returned = store.import_tree(data)

    assert returned is store
    assert [g.display_name for g in store.groups.items] == ["G"]
    group = store.groups.items[0]
    assert [s.display_name for s in group.sets.items] == ["S"]
    assert [t.display_name for t in group.sets.items[0].children.items] == ["T"]


def test_store_manager_import_tree_returns_store():
    store = _store_with(_FakeGroups())

    assert StoreManager(store).import_tree([{"name": "G"}]) is store


# ---------------------------------------------------------------------------
# Naming contract
# ---------------------------------------------------------------------------


def test_store_never_shadows_the_payload_to_json():
    assert "to_json" not in Store.__dict__
    assert Store.to_json is ClientObject.to_json


def test_store_manager_legacy_names_are_deprecated_aliases():
    manager = StoreManager(_store_with(_sample_tree()))

    with pytest.warns(DeprecationWarning, match=r"StoreManager\.to_json"):
        assert manager.to_json().value == EXPECTED_TREE

    with pytest.warns(DeprecationWarning, match=r"StoreManager\.from_json"):
        assert manager.from_json([{"name": "G"}]) is manager.store


def test_store_legacy_from_json_is_a_deprecated_alias():
    store = _store_with(_FakeGroups())

    with pytest.warns(DeprecationWarning, match=r"Store\.from_json"):
        assert store.from_json([{"name": "G"}]) is store
