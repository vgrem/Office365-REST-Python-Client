"""Merged unit tests (consolidated; see git history for originals)."""

from __future__ import annotations

import io
import unittest
import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import cast

from office365.communications.callrecords.call_record import CallRecord
from office365.communications.callrecords.type import CallType
from office365.directory.users.password_profile import PasswordProfile
from office365.directory.users.profile import UserProfile
from office365.directory.users.user import User
from office365.runtime.client_object import ClientObject
from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_result import ClientResult
from office365.runtime.client_runtime_context import ClientRuntimeContext
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.converters.csv_writer import write_csv
from office365.runtime.converters.records import iter_records
from office365.runtime.converters.scalars import iso_z, parse_datetime, parse_int
from office365.runtime.converters.value import _add_type_metadata, declared_type, deserialize_value, serialize_value
from office365.runtime.odata.v3.json_light_format import JsonLightFormat
from office365.runtime.odata.v4.json_format import V4JsonFormat
from office365.runtime.types.collections import StringCollection
from office365.search.hits.container import SearchHitsContainer
from office365.search.response import SearchResponse
from office365.sharepoint.sitedesigns.metadata import SiteDesignMetadata


class TestScalarConverters(unittest.TestCase):
    def test_parse_datetime_iso(self):
        self.assertEqual(parse_datetime("2025-01-15T12:34:56Z"), datetime(2025, 1, 15, 12, 34, 56, tzinfo=timezone.utc))
        self.assertEqual(parse_datetime("2025-01-15T12:34:56"), datetime(2025, 1, 15, 12, 34, 56))

    def test_parse_datetime_numeric_offset(self):
        value = "2025-01-15T12:34:56+00:00"
        parsed = parse_datetime(value)
        assert parsed is not None
        self.assertEqual(parsed.timetuple()[:6], (2025, 1, 15, 12, 34, 56))
        self.assertIsNotNone(parsed.tzinfo)

    def test_parse_datetime_offset_with_microseconds(self):
        value = "2025-01-15T12:34:56.123456+00:00"
        parsed = parse_datetime(value)
        assert parsed is not None
        self.assertEqual(parsed.microsecond, 123456)

    def test_parse_datetime_round_trip(self):
        value = datetime(2025, 1, 15, 12, 34, 56, 123456, tzinfo=timezone.utc)
        self.assertEqual(parse_datetime(value.isoformat()), value)

    def test_parse_datetime_naive_round_trip(self):
        value = datetime(2025, 1, 15, 12, 34, 56)
        self.assertEqual(parse_datetime(value.isoformat()), value)

    def test_iso_z_utc(self):
        value = datetime(2025, 1, 15, 12, 34, 56, 123456, tzinfo=timezone.utc)
        self.assertEqual(iso_z(value), "2025-01-15T12:34:56Z")

    def test_iso_z_converts_non_utc_offset(self):
        value = datetime(2025, 1, 15, 14, 34, 56, tzinfo=timezone(timedelta(hours=2)))
        self.assertEqual(iso_z(value), "2025-01-15T12:34:56Z")

    def test_iso_z_naive_assumed_utc(self):
        value = datetime(2025, 1, 15, 12, 34, 56)
        self.assertEqual(iso_z(value), "2025-01-15T12:34:56Z")

    def test_iso_z_none(self):
        self.assertIsNone(iso_z(None))


class value__Level(Enum):
    Standard = "standard"
    Premium = "premium"


def _new_user(properties: dict) -> User:
    col = ClientObjectCollection(cast(ClientRuntimeContext, None), User, None)
    return col.create_typed_object(properties)


class TestSerializeValue(unittest.TestCase):
    def test_nested_client_value(self):
        profile = PasswordProfile(password="x", forceChangePasswordNextSignIn=True)
        self.assertEqual(serialize_value(profile), {"password": "x", "forceChangePasswordNextSignIn": True})


class TestClientValueToJson(unittest.TestCase):
    def test_user_profile(self):
        profile = UserProfile()
        profile.set_property("accountEnabled", True)
        profile.set_property("passwordProfile", {"password": "x", "forceChangePasswordNextSignIn": True})
        json = profile.to_json()
        assert isinstance(json, dict)
        self.assertIs(json["accountEnabled"], True)
        self.assertEqual(json["passwordProfile"], {"password": "x", "forceChangePasswordNextSignIn": True})

    def test_collection_to_json(self):
        self.assertEqual(StringCollection(["a", "b"]).to_json(), ["a", "b"])
        self.assertEqual(ClientValueCollection(value__Level, [value__Level.Standard]).to_json(), ["standard"])


class TestClientObjectToJson(unittest.TestCase):
    def test_user(self):
        user = _new_user({"accountEnabled": True, "userPrincipalName": "a@b.c"})
        self.assertEqual(user.to_json(), {"accountEnabled": True, "userPrincipalName": "a@b.c"})


class TestAddTypeMetadata(unittest.TestCase):
    def test_json_light(self):
        fmt = JsonLightFormat()
        result: dict = {}
        _add_type_metadata(result, fmt, "Microsoft.Graph.User")
        self.assertEqual(result[fmt.metadata_type], {"type": "Microsoft.Graph.User"})

    def test_plain_odata(self):
        fmt = V4JsonFormat()
        result: dict = {}
        _add_type_metadata(result, fmt, "Microsoft.Graph.User")
        self.assertEqual(result[fmt.metadata_type], "#Microsoft.Graph.User")


class TestDeclaredType(unittest.TestCase):
    def test_entity_getter(self):
        self.assertEqual(declared_type(User, "accountEnabled"), bool)
        self.assertIs(declared_type(User, "createdDateTime"), datetime)

    def test_entity_odata_meta(self):
        self.assertEqual(declared_type(User, "passwordProfile"), PasswordProfile)

    def test_dataclass_datetime_field(self):
        from office365.directory.audit.signins.activity import SignInActivity

        self.assertIs(declared_type(SignInActivity, "lastSignInDateTime"), datetime)
        self.assertIs(declared_type(SignInActivity, "lastSuccessfulSignInDateTime"), datetime)

    def test_sign_in_activity_parses_datetime(self):
        from office365.directory.audit.signins.activity import SignInActivity

        activity = SignInActivity()
        activity.set_property("lastSignInDateTime", "2024-01-01T12:00:00Z")
        self.assertIsInstance(activity.lastSignInDateTime, datetime)
        self.assertEqual(activity.lastSignInDateTime, datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc))

    def test_dataclass_field(self):
        self.assertEqual(declared_type(UserProfile, "userPrincipalName"), str)
        self.assertEqual(declared_type(UserProfile, "accountEnabled"), bool)
        self.assertEqual(declared_type(PasswordProfile, "forceChangePasswordNextSignIn"), bool)

    def test_entity_reserved_word_getter(self):
        # ``CallRecord.type`` is exposed as ``type_`` (a reserved word), which
        # ``to_snake_case`` cannot derive — the trailing-underscore fallback must.
        self.assertIs(declared_type(CallRecord, "type"), CallType)
        record = CallRecord(cast(ClientRuntimeContext, None))
        record.set_property("type", "groupCall")
        self.assertIs(record.type_, CallType.groupCall)


class TestCoerceValue(unittest.TestCase):
    def test_nested_client_value(self):
        current = PasswordProfile()
        result = deserialize_value(
            PasswordProfile, {"password": "x", "forceChangePasswordNextSignIn": "True"}, current, True
        )
        self.assertIs(result, current)
        self.assertEqual(current.password, "x")
        self.assertIs(current.forceChangePasswordNextSignIn, True)

    def test_generic_collection(self):
        response = SearchResponse()
        response.set_property("hitsContainers", [{"hits": [{"contentSource": "x"}], "total": 1}])
        self.assertIsInstance(response.hitsContainers[0], SearchHitsContainer)
        self.assertEqual(response.hitsContainers[0].hits[0].contentSource, "x")


class TestClientResultCoercion(unittest.TestCase):
    def test_enum_keep_on_fail(self):
        result = ClientResult(cast(ClientRuntimeContext, cast(object, None)), value__Level.Standard)
        result.set_property("__value", "nope")
        self.assertIs(result.value, value__Level.Standard)

    def test_enum_valid(self):
        result = ClientResult(cast(ClientRuntimeContext, None), value__Level.Standard)
        result.set_property("__value", "premium")
        self.assertIs(result.value, value__Level.Premium)

    def test_enum_getter_default_does_not_discard_unknown(self):
        class _Widget(ClientObject):
            @property
            def level(self):
                # A getter default (like a generated enum property whose
                # annotation is TYPE_CHECKING-only) must not drive enum
                # coercion for an unrecognized server value.
                return self.properties.get("level", value__Level.Standard)

        widget = _Widget(cast(ClientRuntimeContext, None))
        widget.set_property("level", "mystery")
        self.assertEqual(widget.properties.get("level"), "mystery")

    def test_datetime_keep_on_fail(self):
        result = ClientResult(cast(ClientRuntimeContext, None), datetime(2020, 1, 1))
        result.set_property("__value", "garbage")
        self.assertEqual(result.value, datetime(2020, 1, 1))

    def test_scalar(self):
        result = ClientResult(cast(ClientRuntimeContext, None), "default")
        result.set_property("__value", "hello")
        self.assertEqual(result.value, "hello")

    def test_parse_int(self):
        self.assertEqual(parse_int("42"), 42)
        self.assertEqual(parse_int(7), 7)
        self.assertIsNone(parse_int(None))
        self.assertIsNone(parse_int("abc"))


def _collection(properties: list[dict]) -> ClientObjectCollection:
    col = ClientObjectCollection(cast(ClientRuntimeContext, None), User, None)
    for props in properties:
        col.add_child(col.create_typed_object(props))
    return col


class TestIterRecords(unittest.TestCase):
    def test_plain_select(self):
        col = _collection(
            [
                {"userPrincipalName": "jdoe@contoso.com", "displayName": "John Doe", "accountEnabled": True},
                {"userPrincipalName": "asmith@contoso.com", "displayName": "Alice Smith", "accountEnabled": False},
            ]
        )
        col.query_options.select = ["displayName", "userPrincipalName"]
        self.assertEqual(
            iter_records(col),
            [
                {"displayName": "John Doe", "userPrincipalName": "jdoe@contoso.com"},
                {"displayName": "Alice Smith", "userPrincipalName": "asmith@contoso.com"},
            ],
        )

    def test_native_values_kept(self):
        col = _collection(
            [
                {
                    "displayName": "John",
                    "accountEnabled": True,
                    "createdDateTime": datetime(2025, 1, 15, tzinfo=timezone.utc),
                }
            ]
        )
        col.query_options.select = ["displayName", "accountEnabled", "createdDateTime"]
        record = iter_records(col)[0]
        self.assertIs(record["accountEnabled"], True)
        self.assertEqual(record["createdDateTime"], "2025-01-15T00:00:00+00:00")

    def test_no_select_all_props_sorted(self):
        col = _collection([{"b": 2, "a": 1}])
        self.assertEqual(list(iter_records(col)[0].keys()), ["a", "b"])

    def test_selected_but_missing_key_is_none_filled(self):
        col = _collection([{"displayName": "John"}])
        col.query_options.select = ["displayName", "mail"]
        self.assertEqual(iter_records(col), [{"displayName": "John", "mail": None}])

    def test_multiple_navs_raises(self):
        col = _collection([{"displayName": "John"}])
        col.query_options.select = ["members/displayName", "manager/displayName"]
        with self.assertRaises(ValueError):
            iter_records(col)

    def test_empty_collection(self):
        self.assertEqual(iter_records(_collection([])), [])

    def test_csv_parity(self):
        col = _collection(
            [
                {"displayName": "John", "accountEnabled": True, "businessPhones": ["+1-555-0101", "+1-555-0102"]},
            ]
        )
        col.query_options.select = ["displayName", "accountEnabled", "businessPhones"]
        out = io.StringIO()
        write_csv(col, out)
        self.assertEqual(
            out.getvalue(),
            "displayName,accountEnabled,businessPhones\r\nJohn,True,+1-555-0101; +1-555-0102\r\n",
        )


class TestSiteDesignMetadataDefaults(unittest.TestCase):
    """ClientValueCollection-typed fields keep their item type from defaults."""

    def test_parses_non_empty_site_script_ids(self):
        design = SiteDesignMetadata()
        design.set_property(
            "SiteScriptIds",
            ["07702c07-0485-426f-b710-4704241caad9", "6250ceba-8724-4fb4-8c52-5a89183b9587"],
        )

        assert isinstance(design.SiteScriptIds, ClientValueCollection)
        assert len(design.SiteScriptIds) == 2  # noqa: PLR2004
        assert all(isinstance(item, uuid.UUID) for item in design.SiteScriptIds)

    def test_parses_empty_collection(self):
        design = SiteDesignMetadata()
        design.set_property("SiteScriptIds", [])
        assert isinstance(design.SiteScriptIds, ClientValueCollection)
        assert len(design.SiteScriptIds) == 0
