"""Unit tests for the limits facade + catalog registry (``office365.limits``)."""

from __future__ import annotations

import pytest
from office365 import limits
from office365.communications.callrecords.call_record import CallRecord  # noqa: F401 — registers quotas
from office365.directory.objects.object import DirectoryObject  # noqa: F401 — registers quotas
from office365.sharepoint.thresholds import Limits


def test_sharepoint_catalog_registered():
    assert limits.catalog("sharepoint") == list(Limits.catalog())
    assert any(limit.name == "list view threshold" for limit in limits.catalog("sharepoint"))


def test_model_quotas_registered_by_decorator():
    names = {limit.name for limit in limits.catalog("model")}
    assert "identity" in names  # DirectoryObject
    assert "call records" in names  # CallRecord


def test_catalog_aggregates_and_dedupes():
    all_limits = limits.catalog()
    assert len(all_limits) == len({id(limit) for limit in all_limits})
    assert len(all_limits) >= len(limits.catalog("sharepoint"))


def test_register_catalog_rejects_bad_source():
    limits.register_catalog(object(), product="bad")
    with pytest.raises(TypeError, match="not a Limit catalog"):
        limits.catalog("bad")
