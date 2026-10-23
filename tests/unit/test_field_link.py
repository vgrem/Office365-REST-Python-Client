"""Offline tests for content type field links."""

from __future__ import annotations

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.contenttypes.fieldlinks.field_link import FieldLink
from tests import test_site_url


def _link(**props) -> FieldLink:
    link = FieldLink(ClientContext(test_site_url))
    for name, value in props.items():
        link.set_property(name, value)
    return link


def test_field_internal_name_prefers_explicit_property():
    assert _link(Name="Title", FieldInternalName="Custom").field_internal_name == "Custom"
