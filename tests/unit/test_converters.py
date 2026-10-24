"""Merged unit tests (consolidated; see git history for originals)."""

from __future__ import annotations

import unittest
import uuid
from datetime import datetime, timedelta, timezone
from typing import cast

from office365.communications.callrecords.call_record import CallRecord
from office365.communications.callrecords.type import CallType
from office365.directory.users.password_profile import PasswordProfile
from office365.directory.users.profile import UserProfile
from office365.directory.users.user import User
from office365.outlook.calendar.dateTimeTimeZone import DateTimeTimeZone
from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_runtime_context import ClientRuntimeContext
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.converters.records import iter_records
from office365.runtime.converters.scalars import parse_datetime, parse_int
from office365.runtime.converters.value import coerce_value, declared_type, serialize_value
from office365.runtime.odata.v3.json_light_format import JsonLightFormat
from office365.runtime.odata.v4.json_format import V4JsonFormat
from office365.search.hits.container import SearchHitsContainer
from office365.search.response import SearchResponse
from office365.sharepoint.sitedesigns.metadata import SiteDesignMetadata


class TestScalarConverters(unittest.TestCase):
    def test_parse_datetime_offset_with_microseconds(self):
        value = "2025-01-15T12:34:56.123456+00:00"
        parsed = parse_datetime(value)
        assert parsed is not None
        self.assertEqual(parsed.microsecond, 123456)

    def test_parse_datetime_with_seven_fraction_digits(self):
        """A .NET stamp carries seven digits; the fraction is truncated, not refused."""
        parsed = parse_datetime("2026-10-21T09:05:30.0000000+02:00")
        assert parsed is not None
        self.assertEqual(parsed, datetime(2026, 10, 21, 9, 5, 30, tzinfo=timezone(timedelta(hours=2))))
        self.assertEqual(parse_datetime("2026-10-21T09:05:30.1234567Z").microsecond, 123456)


def _new_user(properties: dict) -> User:
    col = ClientObjectCollection(cast(ClientRuntimeContext, None), User, None)
    return col.create_typed_object(properties)


class TestSerializeValue(unittest.TestCase):
    def test_nested_client_value(self):
        profile = PasswordProfile(password="x", forceChangePasswordNextSignIn=True)
        self.assertEqual(serialize_value(profile), {"password": "x", "forceChangePasswordNextSignIn": True})

    def test_int_enum_serialization_is_format_dependent(self):
        # SharePoint (OData V3) enums are Edm.Int32 -> numeric value.
        from office365.sharepoint.fields.type import FieldType

        self.assertEqual(serialize_value(FieldType.Text, JsonLightFormat()), 2)
        # OData V4 / Graph enums keep the member name.
        self.assertEqual(serialize_value(FieldType.Text, V4JsonFormat()), "Text")
        self.assertEqual(serialize_value(FieldType.Text), "Text")


class TestClientValueToJson(unittest.TestCase):
    def test_user_profile(self):
        profile = UserProfile()
        profile.set_property("accountEnabled", True)
        profile.set_property("passwordProfile", {"password": "x", "forceChangePasswordNextSignIn": True})
        json = profile.to_json()
        assert isinstance(json, dict)
        self.assertIs(json["accountEnabled"], True)
        self.assertEqual(json["passwordProfile"], {"password": "x", "forceChangePasswordNextSignIn": True})

    def test_internal_bookkeeping_is_not_a_field(self):
        # ``__etag`` is ingested from a response so ``If-Match`` can be built; it
        # describes the response, so it must not appear in a serialized value.
        profile = UserProfile()
        profile.set_property("__etag", 'W/"1"')
        profile.set_property("displayName", "A")
        serialized = profile.to_json()
        self.assertNotIn("__etag", serialized)
        self.assertEqual(serialized["displayName"], "A")


class TestClientObjectToJson(unittest.TestCase):
    def test_internal_bookkeeping_never_reaches_the_payload(self):
        # A response bag carries ``__etag``/``__odata_type``/``__deferred``; a request
        # body must not, in either dialect.
        user = _new_user({"__etag": 'W/"1"', "__deferred": {"uri": "x"}, "accountEnabled": True})
        self.assertEqual(user.to_json(), {"accountEnabled": True})
        for json_format in (V4JsonFormat(), JsonLightFormat()):
            serialized = user.to_json(json_format)
            self.assertEqual(serialized["accountEnabled"], True)
            for ingested in ("__etag", "__deferred", "__odata_type"):
                self.assertNotIn(ingested, serialized)
        # The dialect's own control marker is rebuilt after the filter, so it survives
        # while the response's is gone.
        self.assertEqual(user.to_json(JsonLightFormat())["__metadata"], {"type": "microsoft.graph.User"})


class TestDateTimeTimeZone(unittest.TestCase):
    def test_a_datetime_becomes_the_canonical_wire_form(self):
        # Graph reads `dateTime` as a wall clock and takes the zone from `timeZone`,
        # so the fraction is Graph's seven digits and no offset is appended.
        value = DateTimeTimeZone.parse(datetime(2026, 5, 4, 9, 0))
        self.assertEqual(value.dateTime, "2026-05-04T09:00:00.0000000")
        self.assertEqual(value.timeZone, "UTC")
        self.assertEqual(value.to_json(), {"dateTime": "2026-05-04T09:00:00.0000000", "timeZone": "UTC"})

    def test_as_datetime_reads_the_wall_clock(self):
        value = DateTimeTimeZone(dateTime="2026-05-04T07:00:00.0000000", timeZone="UTC")
        self.assertEqual(value.as_datetime(), datetime(2026, 5, 4, 7, 0))
        self.assertIsNone(DateTimeTimeZone().as_datetime())
        self.assertIsNone(DateTimeTimeZone(dateTime="not a date").as_datetime())


class TestDeclaredType(unittest.TestCase):
    def test_entity_getter(self):
        self.assertEqual(declared_type(User, "accountEnabled"), bool)
        self.assertIs(declared_type(User, "createdDateTime"), datetime)

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
        result = coerce_value(PasswordProfile, {"password": "x", "forceChangePasswordNextSignIn": "True"}, current, True)
        self.assertIs(result, current)
        self.assertEqual(current.password, "x")
        self.assertIs(current.forceChangePasswordNextSignIn, True)

    def test_generic_collection(self):
        response = SearchResponse()
        response.set_property("hitsContainers", [{"hits": [{"contentSource": "x"}], "total": 1}])
        self.assertIsInstance(response.hitsContainers[0], SearchHitsContainer)
        self.assertEqual(response.hitsContainers[0].hits[0].contentSource, "x")


class TestClientResultCoercion(unittest.TestCase):
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
