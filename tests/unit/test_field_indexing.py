"""Unit tests for column indexing (list view threshold mitigation)."""

from __future__ import annotations

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.fields.field import Field
from tests import test_site_url


def test_field_ensure_indexed_queues_enable():
    ctx = ClientContext(test_site_url)
    field = Field(ctx)
    field.set_property("Indexed", False)

    field.ensure_indexed()

    assert len(ctx._queries) == 1  # enableIndex was queued
    assert field.properties["Indexed"] is False  # only the server flips it
