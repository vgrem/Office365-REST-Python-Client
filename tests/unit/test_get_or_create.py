"""Tests for the shared idempotent get-or-create primitives."""

from __future__ import annotations

from office365.runtime.queries.get_or_create import get_or_create


class _FakeContext:
    def __init__(self) -> None:
        self._queries: list[object] = []

    def add_query(self, query):
        self._queries.append(query)
        return self


class _FakeEntity:
    def __init__(self, context: _FakeContext) -> None:
        self.context = context
        self._after: list = []
        self._error: list = []
        self.copied_from = None
        self.updated = False

    def after_execute(self, action, execute_first=False):
        self._after.append(action)
        return self

    def on_error(self, action):
        self._error.append(action)
        return self

    def copy_from(self, other):
        self.copied_from = other

    def update(self):
        self.updated = True


def test_get_or_create_returns_existing_when_found():
    ctx = _FakeContext()
    return_type = _FakeEntity(ctx)
    found = _FakeEntity(ctx)

    result = get_or_create(find=lambda: found, create_query=object, return_type=return_type)

    assert result is return_type
    found._after[0](found)
    assert return_type.copied_from is found
    assert ctx._queries == []  # the placeholder resolved (no create)


def test_get_or_create_tolerant_miss_defers_create():
    ctx = _FakeContext()
    return_type = _FakeEntity(ctx)
    found = _FakeEntity(ctx)
    create_query = object()

    get_or_create(
        find=lambda: found,
        create_query=lambda: create_query,
        return_type=return_type,
        missing=lambda entity: True,
    )
    barrier = ctx._queries[-1]
    found._after[0](found)

    assert create_query in ctx._queries
    assert barrier not in ctx._queries
    assert return_type.copied_from is None
