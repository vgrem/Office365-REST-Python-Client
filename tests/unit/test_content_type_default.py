"""Offline tests for a list's default content type (root folder order)."""

from __future__ import annotations

import pytest
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.contenttypes.content_type import ContentType, _content_type_order_ids
from office365.sharepoint.contenttypes.content_type_id import ContentTypeId
from tests import test_site_url


def test_order_ids_from_flattened_value():
    # The folder property is typed as a single ContentTypeId, so a server-side
    # Collection(SP.ContentTypeId) arrives flattened under numeric keys.
    order = ContentTypeId()
    order.set_property(0, {"StringValue": "0x02"})
    order.set_property(1, {"StringValue": "0x01"})
    assert _content_type_order_ids(order) == ["0x02", "0x01"]


def test_set_default_requires_list_scope():
    content_type = ContentType(ClientContext(test_site_url))
    with pytest.raises(ValueError):
        content_type.set_default()
