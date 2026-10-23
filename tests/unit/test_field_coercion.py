"""Unit tests for typed SharePoint field value coercion (``schema={col: FieldType}``)."""

from __future__ import annotations

from datetime import datetime

from office365.sharepoint.fields.coercion import coerce_field_value
from office365.sharepoint.fields.geolocation_value import FieldGeolocationValue
from office365.sharepoint.fields.lookup_value import FieldLookupValue
from office365.sharepoint.fields.multi_lookup_value import FieldMultiLookupValue
from office365.sharepoint.fields.multi_user_value import FieldMultiUserValue
from office365.sharepoint.fields.type import FieldType
from office365.sharepoint.fields.url_value import FieldUrlValue
from office365.sharepoint.fields.user_value import FieldUserValue


def test_user_from_email_id_and_list():
    from_email = coerce_field_value(FieldType.User, "alice@contoso.com")
    from_id = coerce_field_value(FieldType.User, 7)
    multi = coerce_field_value(FieldType.User, [1, 2])

    assert isinstance(from_email, FieldUserValue)
    assert from_email.Email == "alice@contoso.com"
    assert from_id.LookupId == 7  # noqa: PLR2004
    assert isinstance(multi, FieldMultiUserValue)
    assert [item.LookupId for item in multi] == [1, 2]


def test_url_from_string_and_pair():
    plain = coerce_field_value(FieldType.URL, "https://contoso.com")
    pair = coerce_field_value(FieldType.URL, ("https://contoso.com", "Contoso"))

    assert isinstance(plain, FieldUrlValue)
    assert plain.Url == "https://contoso.com"
    assert pair.Description == "Contoso"


def test_geolocation_from_string_and_pair():
    from_string = coerce_field_value(FieldType.Geolocation, "51.5,-0.12")
    from_pair = coerce_field_value(FieldType.Geolocation, (51.5, -0.12))

    assert isinstance(from_string, FieldGeolocationValue)
    assert from_string.Latitude == 51.5  # noqa: PLR2004
    assert from_pair.Longitude == -0.12  # noqa: PLR2004


def test_scalar_coercions():
    assert coerce_field_value(FieldType.Boolean, "yes") is True
    assert coerce_field_value(FieldType.Boolean, "0") is False
    assert coerce_field_value(FieldType.Number, "3.5") == 3.5  # noqa: PLR2004
    assert coerce_field_value(FieldType.Integer, "12") == 12  # noqa: PLR2004
    assert coerce_field_value(FieldType.DateTime, "2024-01-02") == datetime(2024, 1, 2)


def test_listitem_persists_multi_user_and_lookup_ids():
    from office365.sharepoint.client_context import ClientContext
    from office365.sharepoint.listitems.listitem import ListItem

    item = ListItem(ClientContext("https://contoso.sharepoint.com/sites/x"))
    item.set_property("MultiOwner", FieldMultiUserValue([FieldUserValue(12), FieldUserValue(7)]))
    item.set_property("MultiDept", FieldMultiLookupValue([FieldLookupValue(2), FieldLookupValue(3)]))

    # A multi-value column persists its ``<name>Id`` collection; ``<name>`` itself
    # is transient. ``FieldMultiUserValue`` must be handled like ``FieldMultiLookupValue``
    # (regression: it used to be written as ``<name>`` only, so the user ids were lost).
    assert list(item.properties["MultiOwnerId"]) == [12, 7]
    assert list(item.properties["MultiDeptId"]) == [2, 3]
    assert item.to_json()["MultiOwnerId"] == [12, 7]
    assert item.to_json()["MultiDeptId"] == [2, 3]
