"""Unit tests for the limits facade + catalog registry (``office365.limits``)."""

from __future__ import annotations

from office365 import limits
from office365.communications.callrecords.call_record import CallRecord  # noqa: F401 — registers quotas
from office365.directory.objects.object import DirectoryObject  # noqa: F401 — registers quotas


def test_catalog_aggregates_and_dedupes():
    all_limits = limits.catalog()
    assert len(all_limits) == len({id(limit) for limit in all_limits})
    assert len(all_limits) >= len(limits.catalog("sharepoint"))
