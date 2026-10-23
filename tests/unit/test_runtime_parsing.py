"""Merged unit tests (consolidated; see git history for originals)."""

from __future__ import annotations

import json
import unittest
from datetime import datetime, timezone
from enum import Enum

from office365.directory.applications.application import Application
from office365.directory.groups.group import Group
from office365.directory.objects.collection import DirectoryObjectCollection
from office365.directory.objects.object import DirectoryObject
from office365.directory.serviceprincipals.service_principal import ServicePrincipal
from office365.directory.users.user import User
from office365.entity import Entity
from office365.graph_client import GraphClient
from office365.intune.devices.device import Device
from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.odata.query_options import QueryOptions
from office365.runtime.odata.request import ODataRequest
from office365.runtime.odata.v3.json_light_format import JsonLightFormat
from office365.runtime.odata.v4.json_format import V4JsonFormat
from office365.runtime.queries.client_query import ClientQuery
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.read_entity import ReadEntityQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.odata_property import odata
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.exceptions import SPQueryThrottledException
from requests import Response
from tests import test_site_url


class TestResponseParsing(unittest.TestCase):
    """A malformed body must surface as ClientRequestException, not ValueError."""

    def test_malformed_json_raises_client_request_exception(self):
        ctx = ClientContext(test_site_url)
        request = ODataRequest(test_site_url, JsonLightFormat())
        query = ClientQuery(ctx, return_type=ClientResult(ctx))

        resp = Response()
        resp.status_code = 200
        resp.url = f"{test_site_url}/_api/web"
        resp.headers["Content-Type"] = "application/json"
        resp._content = b"<html><body>Expired form digest</body></html>"

        with self.assertRaises(ClientRequestException) as cm:
            request.handle_response(resp, query)

        self.assertIs(cm.exception.response, resp)

    def test_raw_content_query_returns_bytes_for_json(self):
        """A raw-content query (e.g. OneDrive /content) must return bytes even when the
        downloaded file is JSON and the server reports application/json."""
        ctx = ClientContext(test_site_url)
        request = ODataRequest(test_site_url, JsonLightFormat())
        result = ClientResult(ctx, bytes())
        query = FunctionQuery(ctx.web, "content", return_type=result, return_raw_content=True)

        resp = Response()
        resp.status_code = 200
        resp.headers["Content-Type"] = "application/json"
        resp._content = b'{"name": "test", "version": 1}'

        request.handle_response(resp, query)
        self.assertEqual(result.value, b'{"name": "test", "version": 1}')

    def test_raw_content_returns_bytes_for_octet_stream(self):
        """Non-JSON content types keep returning raw bytes without the flag."""
        ctx = ClientContext(test_site_url)
        request = ODataRequest(test_site_url, JsonLightFormat())
        result = ClientResult(ctx, bytes())
        query = FunctionQuery(ctx.web, "$value", return_type=result)

        resp = Response()
        resp.status_code = 200
        resp.headers["Content-Type"] = "application/octet-stream"
        resp._content = b"\x00\x01\x02"

        request.handle_response(resp, query)
        self.assertEqual(result.value, b"\x00\x01\x02")


def _make_error_response(body: dict, headers: dict | None = None) -> Response:
    resp = Response()
    resp.status_code = 400
    resp.url = "https://contoso.sharepoint.com/_api/web/lists"
    resp.headers.update(headers or {})
    resp._content = json.dumps(body).encode("utf-8")
    return resp


class TestFromResponse(unittest.TestCase):
    def test_nested_json_message_is_unwrapped(self):
        inner = (
            "Application is not authorized to perform this operation. "
            "Application must have one of the following scopes: DeviceManagementApps.Read.All"
        )
        noisy = inner + " - Operation ID (for customer support): 0000 - Activity ID: abc - Url: https://proxy"
        body = {
            "error": {
                "code": "Forbidden",
                "message": json.dumps({"_version": 3, "Message": noisy, "RetryAfter": None}),
            }
        }
        exc = ClientRequestException.from_response(_make_error_response(body))
        self.assertEqual(exc.message, inner)
        self.assertIn(inner, str(exc))
        self.assertNotIn("_version", str(exc))
        self.assertNotIn("Activity ID", str(exc))

    def test_list_view_threshold_maps_to_throttled(self):
        body = {
            "error": {
                "code": "-2147024860, Microsoft.SharePoint.SPQueryThrottledException",
                "message": {
                    "lang": "en-US",
                    "value": "The attempted operation is prohibited because it exceeds the list view threshold.",
                },
            }
        }
        exc = ClientRequestException.from_response(_make_error_response(body))
        self.assertIsInstance(exc, SPQueryThrottledException)
        self.assertIn("list view threshold", str(exc).lower())


class TestDiagnostics(unittest.TestCase):
    def test_graph_inner_error_exposed(self):
        body = {
            "error": {
                "code": "TooManyRequests",
                "message": "Please retry again later.",
                "innerError": {
                    "code": "429",
                    "date": "2025-01-01T00:00:00",
                    "request-id": "94fb3b52-452a-4535-a601-69e0a90e3aa2",
                    "status": "429",
                },
            }
        }
        exc = ClientRequestException.from_response(_make_error_response(body))
        self.assertEqual(exc.request_id, "94fb3b52-452a-4535-a601-69e0a90e3aa2")
        assert exc.inner_error is not None
        self.assertEqual(exc.inner_error["status"], "429")

    def test_sharepoint_headers_exposed(self):
        body = {"error": {"code": "-1, System.Exception", "message": "boom"}}
        exc = ClientRequestException.from_response(
            _make_error_response(
                body,
                headers={
                    "SPRequestGuid": "a1b2c3d4-1234-5678-9abc-def012345678",
                    "SPRequestDuration": "127",
                    "X-SharePointHealthScore": "3",
                },
            )
        )
        self.assertEqual(exc.server_guid, "a1b2c3d4-1234-5678-9abc-def012345678")
        self.assertEqual(exc.duration_ms, 127)  # noqa: PLR2004
        self.assertEqual(exc.health_score, 3)  # noqa: PLR2004

    def test_diagnostics_absent(self):
        exc = ClientRequestException.from_response(_make_error_response({"error": {"message": "boom"}}))
        self.assertIsNone(exc.request_id)
        self.assertIsNone(exc.inner_error)
        self.assertIsNone(exc.server_guid)
        self.assertIsNone(exc.duration_ms)
        self.assertIsNone(exc.health_score)


def _graph_request() -> ODataRequest:
    return ODataRequest("", V4JsonFormat())


class TestODataResponseType(unittest.TestCase):
    """Members are cast to concrete classes from ``@odata.type`` (exposed via ``entity_type_name``)."""

    def test_members_are_cast_to_concrete_types(self):
        ctx = ClientContext(test_site_url)
        payload = {
            "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#directoryObjects",
            "value": [
                {"@odata.type": "#microsoft.graph.user", "id": "u1", "displayName": "Alice"},
                {"@odata.type": "#microsoft.graph.group", "id": "g1"},
                {"@odata.type": "#microsoft.graph.device", "id": "d1"},
                {"@odata.type": "#microsoft.graph.application", "id": "a1"},
                {"@odata.type": "#microsoft.graph.servicePrincipal", "id": "sp1"},
            ],
        }
        col = DirectoryObjectCollection(ctx)
        _graph_request().hydrate(col, payload, V4JsonFormat())

        self.assertEqual(len(col), 5)  # noqa: PLR2004
        self.assertIsInstance(col[0], User)
        self.assertIsInstance(col[1], Group)
        self.assertIsInstance(col[2], Device)
        self.assertIsInstance(col[3], Application)
        self.assertIsInstance(col[4], ServicePrincipal)
        self.assertEqual(col[0].entity_type_name, "microsoft.graph.User")
        self.assertEqual(col[0].get_property("displayName"), "Alice")
        for item in col:
            self.assertNotIn("@odata.type", item.properties)
            self.assertNotIn("__odata_type", item.properties)

    def test_unknown_member_type_falls_back_to_directory_object(self):
        ctx = ClientContext(test_site_url)
        payload = {"value": [{"@odata.type": "#microsoft.graph.administrativeUnit", "id": "au1"}]}
        col = DirectoryObjectCollection(ctx)
        _graph_request().hydrate(col, payload, V4JsonFormat())

        self.assertEqual(len(col), 1)
        self.assertIsInstance(col[0], DirectoryObject)
        self.assertNotIn("__odata_type", col[0].properties)

    def test_single_entity_keeps_class_type(self):
        ctx = ClientContext(test_site_url)
        payload = {"@odata.type": "#microsoft.graph.user", "id": "u1", "displayName": "Alice"}
        user = User(ctx)
        _graph_request().hydrate(user, payload, V4JsonFormat())

        self.assertEqual(user.entity_type_name, "microsoft.graph.User")
        self.assertEqual(user.get_property("id"), "u1")
        self.assertNotIn("@odata.type", user.properties)
        self.assertNotIn("__odata_type", user.properties)

    def test_sharepoint_json_light_metadata_is_untouched(self):
        """JsonLight/SharePoint metadata must not leak into properties or type name."""
        ctx = ClientContext(test_site_url)
        payload = {"d": {"__metadata": {"type": "SP.Web"}, "Id": "web-1", "Url": "https://x"}}
        web = ctx.web
        ODataRequest(test_site_url, JsonLightFormat()).hydrate(web, payload, JsonLightFormat())

        self.assertEqual(web.entity_type_name, "SP.Web")
        self.assertNotIn("__metadata", web.properties)


class TestDeltaToken(unittest.TestCase):
    """Delta requests must use ?token=... and expose a resumable token value."""

    def test_delta_resume_withholds_filter(self):
        delta = GraphClient().me.drive.root.delta
        delta.filter("startswith(name,'A')")
        with self.assertWarns(RuntimeWarning):
            delta.token("abc123")
        self.assertEqual(
            ReadEntityQuery(delta).url,
            "https://graph.microsoft.com/v1.0/me/drive/root/delta?token=abc123",
        )


class TestClientMetadata(unittest.TestCase):
    """Entity type-name resolution, query-option building and ClientResult wrapping."""

    def test_query_options_apply_to(self):
        class _Target:
            def select(self, names):
                self._select = names

            def expand(self, names):
                self._expand = names

        options = QueryOptions(select=["Title"], expand=["Fields"])
        target = _Target()
        options.apply_to(target)
        self.assertEqual(target._select, ["Title"])
        self.assertEqual(target._expand, ["Fields"])

        empty = QueryOptions()
        untouched = _Target()
        empty.apply_to(untouched)
        self.assertFalse(hasattr(untouched, "_select"))
        self.assertFalse(hasattr(untouched, "_expand"))


class TestRequireLicense(unittest.TestCase):
    def _make_client(self) -> GraphClient:
        return GraphClient(tenant="contoso.onmicrosoft.com")


class TestRequireDelegatedPermission(unittest.TestCase):
    def _make_client(self) -> GraphClient:
        ctx = GraphClient(tenant="contoso.onmicrosoft.com")
        ctx.pending_request().authentication_context._client_id = "app-id"
        return ctx


class _MeetingMode(Enum):
    enabled = "enabled"
    disabled = "disabled"


class TestQueryPayloadSerialization(unittest.TestCase):
    """A query payload holding scalars must already be JSON-ready."""

    def test_datetime_and_enum_are_serialized_in_nested_payload(self):
        """Regression: a raw ``datetime`` in a service-operation payload used to reach
        ``json.dumps`` unchanged (``create_or_get`` on online meetings failed with
        "Object of type datetime is not JSON serializable")."""
        ctx = ClientContext(test_site_url)
        start = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
        query = ServiceOperationQuery(
            ctx.web,
            "createOrGet",
            None,
            {
                "startDateTime": start,
                "mode": _MeetingMode.disabled,
                "nested": {"endDateTime": start},
                "items": [start],
                "absent": None,
            },
        )

        payload = ODataRequest(test_site_url, JsonLightFormat())._build_payload(query)

        json.dumps(payload)  # must not raise
        self.assertEqual(payload["startDateTime"], start.isoformat())
        self.assertEqual(payload["mode"], "disabled")
        self.assertEqual(payload["nested"]["endDateTime"], start.isoformat())
        self.assertEqual(payload["items"], [start.isoformat()])
        self.assertNotIn("absent", payload)


class _SortValue:
    """A value that declares a type, spelled the way a ``ClientValue`` would."""

    entity_type_name = "SP.Search.Query.Sort"

    def __init__(self, name: str) -> None:
        self.name = name

    def to_json(self, json_format=None):
        payload = {"name": self.name}
        return json_format.wrap(self, payload) if json_format is not None else payload


class TestBuildPayload(unittest.TestCase):
    """A query body is built by the profile, so it is always spelled for the
    service that will read it — no second, marker-less serializer in the request."""

    def test_collection_items_are_spelled_the_way_the_dialect_spells_them(self):
        collection = ClientValueCollection(_SortValue, [_SortValue("Modified")])
        payload = JsonLightFormat().build_payload({"SortList": collection})
        self.assertEqual(
            payload["SortList"]["results"],
            [{"name": "Modified", "__metadata": {"type": "SP.Search.Query.Sort"}}],
        )
        self.assertEqual(
            payload["SortList"]["__metadata"],
            {"type": "Collection(SP.Search.Query.Sort)"},
        )


class _Drafted(Entity):
    """A model with a service-owned column and a caller-owned one."""

    @odata(name="subject")
    @property
    def subject(self) -> str | None:
        return self.properties.get("subject", None)

    @odata(name="iCalUId", readonly=True)
    @property
    def i_cal_uid(self) -> str | None:
        return self.properties.get("iCalUId", None)


class TestAPropertyTheServiceOwns(unittest.TestCase):
    def test_a_response_is_not_a_draft_and_marks_nothing(self):
        target = _Drafted(GraphClient())
        V4JsonFormat().hydrate(target, {"subject": "Q1"})

        self.assertEqual({}, target.to_json(V4JsonFormat("none")))
        self.assertEqual({"subject": "Q1"}, target.to_json())


class TestReadingAPayloadTheCallerAlreadyHasAnObjectFor(unittest.TestCase):
    """``hydrate`` is the mirror of ``to_json``: the payload is the whole record."""

    def test_it_reads_every_value_the_payload_says(self):
        """A payload read as content is not a response: nothing is left unmarked."""
        target = _Drafted(GraphClient()).hydrate({"subject": "Q1", "iCalUId": "0400"}, V4JsonFormat())

        self.assertEqual({"subject": "Q1"}, target.to_json(V4JsonFormat("none")))
        self.assertEqual({"subject": "Q1", "iCalUId": "0400"}, target.to_json())

    def test_the_profile_decides_how_a_payload_is_read(self):
        """JSON Light wraps an entity in ``d``; the same mapping means nothing to V4."""
        payload = {"d": {"subject": "Q1"}}

        self.assertEqual("Q1", _Drafted(GraphClient()).hydrate(payload, JsonLightFormat()).subject)
        self.assertIsNone(_Drafted(GraphClient()).hydrate(payload, V4JsonFormat()).subject)
