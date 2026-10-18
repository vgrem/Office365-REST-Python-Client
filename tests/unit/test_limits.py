"""Unit tests for the service-limit catalog and guard-rails."""

from __future__ import annotations

import warnings

import pytest
from office365.runtime.client_object import ClientObject
from office365.runtime.limits import (
    Limit,
    LimitExceededError,
    LimitKind,
    bounded,
    ensure_within,
    hint,
    limit,
    limits_of,
    verify_limits,
    warn_if_exceeds,
)
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.thresholds import LIST_VIEW_THRESHOLD, Limits
from tests import test_site_url

LIST_VIEW = Limits.LIST_VIEW


def test_catalog_is_populated_and_well_formed():
    catalog = Limits.catalog()
    assert len(catalog) >= 30  # noqa: PLR2004
    names = [entry.name for entry in catalog]
    assert len(names) == len(set(names))  # unique names
    for entry in catalog:
        assert isinstance(entry, Limit)
        assert isinstance(entry.kind, LimitKind)
        assert entry.value > 0
        assert entry.unit


def test_str_formats_items_and_bytes():
    assert str(LIST_VIEW) == "5,000 items"
    assert str(Limits.FILE_UPLOAD) == "250 GB"
    assert str(Limits.LIST_ROW_BYTES) == "8,000 bytes"


def test_warn_if_exceeds():
    with pytest.warns(UserWarning, match="list view threshold"):
        assert warn_if_exceeds(LIST_VIEW, 6000) is True
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert warn_if_exceeds(LIST_VIEW, 10) is False


def test_ensure_within_raises_by_default():
    with pytest.raises(LimitExceededError) as exc:
        ensure_within(LIST_VIEW, 9000, context="query")
    assert exc.value.limit is LIST_VIEW
    assert exc.value.value == 9000  # noqa: PLR2004
    assert "query" in str(exc.value)


def test_ensure_within_warn_mode_and_passthrough():
    with pytest.warns(UserWarning):
        ensure_within(LIST_VIEW, 9000, on_exceed="warn")
    ensure_within(LIST_VIEW, 10)  # under the limit -> no raise
    with pytest.raises(ValueError, match="on_exceed"):
        ensure_within(LIST_VIEW, 10, on_exceed="nope")


def test_hint_includes_context_and_docs():
    text = hint(LIST_VIEW, context="get_items", value=6000)
    assert "get_items" in text
    assert "6,000 items" in text
    assert "learn.microsoft.com" in text


def test_bounded_warns_by_default():
    @bounded("page_size", LIST_VIEW)
    def get_items(caml_query=None, page_size=None):
        return page_size

    with pytest.warns(UserWarning):
        assert get_items(page_size=6000) == 6000  # noqa: PLR2004
    assert get_items(page_size=2000) == 2000  # noqa: PLR2004
    assert get_items() is None  # None passes


def test_bounded_clamps_and_handles_positional_args():
    @bounded("page_size", LIST_VIEW, clamp=True)
    def get_items(caml_query, page_size):
        return page_size

    assert get_items(None, 6000) == LIST_VIEW.value
    assert get_items(None, 100) == 100  # noqa: PLR2004


def test_list_get_items_warns_when_page_size_over_threshold():
    lst = ClientContext(test_site_url).web.lists.get_by_title("X")
    with pytest.warns(UserWarning, match="list view threshold"):
        lst.get_items(page_size=LIST_VIEW_THRESHOLD + 1)


def test_bounded_raise_mode_and_validation():
    @bounded("page_size", LIST_VIEW, on_exceed="raise")
    def get_items(page_size=None):
        return page_size

    with pytest.raises(LimitExceededError):
        get_items(page_size=6000)
    with pytest.raises(ValueError, match="on_exceed"):
        bounded("page_size", LIST_VIEW, on_exceed="nope")


# ── @limit metadata (bound to methods/properties) ────────────────────────────


def test_limit_decorator_stamps_metadata_and_doc():
    @limit(Limits.FILE_UPLOAD)
    def upload(content):
        """Upload a file."""
        return content

    decls = limits_of(upload)
    assert len(decls) == 1
    assert decls[0].limit is Limits.FILE_UPLOAD
    assert decls[0].arg is None
    assert "Limits:" in upload.__doc__
    assert "file upload" in upload.__doc__


def test_limit_decorator_enforces_arg():
    @limit(Limits.LIST_VIEW, arg="page_size")
    def get_items(page_size=None):
        return page_size

    with pytest.warns(UserWarning, match="list view threshold"):
        assert get_items(page_size=6000) == 6000  # noqa: PLR2004
    assert get_items(page_size=10) == 10  # noqa: PLR2004
    assert get_items() is None


def test_limit_decorator_raise_and_clamp():
    @limit(Limits.LIST_VIEW, arg="page_size", on_exceed="raise")
    def strict(page_size=None):
        return page_size

    with pytest.raises(LimitExceededError):
        strict(page_size=6000)

    @limit(Limits.LIST_VIEW, arg="page_size", clamp=True)
    def clamped(page_size=None):
        return page_size

    assert clamped(page_size=6000) == Limits.LIST_VIEW.value


def test_limit_decorator_on_property_and_class_meta():
    class _Entity(ClientObject):
        @limit(Limits.FILE_UPLOAD)
        @property
        def upload(self):
            return None

        @limit(Limits.LIST_VIEW, arg="page_size")
        def get_items(self, page_size=None):
            return page_size

    assert "upload" in _Entity._limit_meta
    assert "get_items" in _Entity._limit_meta
    assert Limits.FILE_UPLOAD in _Entity.declared_limits()
    assert Limits.LIST_VIEW in _Entity.declared_limits()


def test_limit_requires_single_limit_for_arg():
    with pytest.raises(ValueError, match="exactly one"):
        limit(Limits.LIST_VIEW, Limits.FILE_UPLOAD, arg="page_size")


def test_verify_limits_reports_violations():
    @limit(Limits.LIST_VIEW, arg="page_size")
    def get_items(page_size=None):
        return page_size

    assert verify_limits(get_items, page_size=10).ok
    report = verify_limits(get_items, page_size=6000)
    assert not report.ok
    assert "list view threshold" in str(report)


def test_bounded_back_compat_alias():
    @bounded("page_size", Limits.LIST_VIEW)
    def get_items(page_size=None):
        return page_size

    with pytest.warns(UserWarning):
        assert get_items(page_size=6000) == 6000  # noqa: PLR2004


# ── @limit on a class (model-bound quotas) ───────────────────────────────────


def test_limit_decorator_on_class_and_inheritance():
    @limit(Limits.LIST_VIEW, Limits.FILE_UPLOAD)
    class _Base(ClientObject):
        pass

    class _Child(_Base):
        pass

    assert Limits.LIST_VIEW in _Base.declared_limits()
    assert Limits.FILE_UPLOAD in _Base.declared_limits()
    assert Limits.LIST_VIEW in _Child.declared_limits()  # inherited


def test_limit_on_class_merges_with_base():
    @limit(Limits.LIST_VIEW)
    class _Base(ClientObject):
        pass

    @limit(Limits.FILE_UPLOAD)
    class _Child(_Base):
        pass

    declared = _Child.declared_limits()
    assert Limits.LIST_VIEW in declared
    assert Limits.FILE_UPLOAD in declared


def test_limit_rejects_arg_on_class():
    with pytest.raises(ValueError, match="class"):

        @limit(Limits.LIST_VIEW, arg="page_size")
        class _Bad(ClientObject):
            pass
