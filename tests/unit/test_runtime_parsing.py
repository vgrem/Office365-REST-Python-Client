"""Merged unit tests (consolidated; see git history for originals)."""

from __future__ import annotations

import json
import unittest
from datetime import datetime, timezone
from enum import Enum
from unittest import mock

from office365.delta_collection import DeltaCollection
from office365.directory.applications.application import Application
from office365.directory.groups.group import Group
from office365.directory.objects.collection import DirectoryObjectCollection
from office365.directory.objects.object import DirectoryObject
from office365.directory.serviceprincipals.service_principal import ServicePrincipal
from office365.directory.users.user import User
from office365.graph_client import GraphClient
from office365.intune.devices.device import Device
from office365.onedrive.driveitems.driveItem import DriveItem
from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.client_result import ClientResult
from office365.runtime.exceptions import (
    DuplicatedObjectException,
    ObjectNotFoundException,
)
from office365.runtime.odata.query_options import QueryOptions
from office365.runtime.odata.request import ODataRequest
from office365.runtime.odata.v3.json_light_format import JsonLightFormat
from office365.runtime.odata.v4.json_format import V4JsonFormat
from office365.runtime.queries.client_query import ClientQuery
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.read_entity import ReadEntityQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import StringCollection
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
            request.process_response(resp, query)

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

        request.process_response(resp, query)
        self.assertEqual(result.value, b'{"name": "test", "version": 1}')

    def test_regular_query_still_parses_json(self):
        """Without the raw-content flag, application/json is still parsed as OData JSON."""
        ctx = ClientContext(test_site_url)
        request = ODataRequest(test_site_url, JsonLightFormat())
        result = ClientResult(ctx)
        query = FunctionQuery(ctx.web, "content", return_type=result)

        resp = Response()
        resp.status_code = 200
        resp.headers["Content-Type"] = "application/json"
        resp._content = b'{"name": "test", "version": 1}'

        request.process_response(resp, query)
        self.assertIsNot(result.value, b'{"name": "test", "version": 1}')

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

        request.process_response(resp, query)
        self.assertEqual(result.value, b"\x00\x01\x02")


def _make_error_response(body: dict, headers: dict | None = None) -> Response:
    resp = Response()
    resp.status_code = 400
    resp.url = "https://contoso.sharepoint.com/_api/web/lists"
    resp.headers.update(headers or {})
    resp._content = json.dumps(body).encode("utf-8")
    return resp


class TestFromResponse(unittest.TestCase):
    def test_sharepoint_list_already_exists(self):
        body = {
            "error": {
                "code": "-2130575342, Microsoft.SharePoint.SPException",
                "message": {
                    "lang": "en-US",
                    "value": "A list, survey, discussion board, or document library "
                    "with the specified title already exists in this Web site.",
                },
            }
        }
        exc = ClientRequestException.from_response(_make_error_response(body))
        self.assertIsInstance(exc, DuplicatedObjectException)

    def test_message_fallback_already_exists(self):
        body = {
            "error": {
                "code": "-1, System.Exception",
                "message": "A column with this name already exists.",
            }
        }
        exc = ClientRequestException.from_response(_make_error_response(body))
        self.assertIsInstance(exc, DuplicatedObjectException)

    def test_unrelated_error_stays_generic(self):
        body = {
            "error": {
                "code": "-2147024809, System.ArgumentException",
                "message": "Invalid argument.",
            }
        }
        exc = ClientRequestException.from_response(_make_error_response(body))
        self.assertNotIsInstance(exc, DuplicatedObjectException)
        self.assertIsInstance(exc, ClientRequestException)

    def test_field_not_found_maps_to_object_not_found(self):
        body = {
            "error": {
                "code": "-2147024809, System.ArgumentException",
                "message": {"lang": "en-US", "value": 'Field with name "Status" was not found.'},
            }
        }
        exc = ClientRequestException.from_response(_make_error_response(body))
        self.assertIsInstance(exc, ObjectNotFoundException)

    def test_other_errors_not_duplicated(self):
        body = {
            "error": {
                "code": "-2147024894, System.IO.FileNotFoundException",
                "message": "ResourceNotFound",
            }
        }
        exc = ClientRequestException.from_response(_make_error_response(body))
        self.assertNotIsInstance(exc, DuplicatedObjectException)

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

    def test_throttled_localized_message_matches_by_code(self):
        body = {
            "error": {
                "code": "-2147024860, Microsoft.SharePoint.SPQueryThrottledException",
                "message": (
                    "La operación que se intentó realizar está prohibida porque supera el umbral de vista de lista."
                ),
            }
        }
        exc = ClientRequestException.from_response(_make_error_response(body))
        self.assertIsInstance(exc, SPQueryThrottledException)
        self.assertIn("get_all", str(exc))  # actionable guidance is appended


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

    def test_request_id_prefers_headers(self):
        body = {
            "error": {
                "code": "BadRequest",
                "message": "bad",
                "innerError": {"request-id": "from-body"},
            }
        }
        exc = ClientRequestException.from_response(
            _make_error_response(body, headers={"client-request-id": "from-header"})
        )
        self.assertEqual(exc.request_id, "from-header")

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
        _graph_request().map_json(payload, col, V4JsonFormat())

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
        _graph_request().map_json(payload, col, V4JsonFormat())

        self.assertEqual(len(col), 1)
        self.assertIsInstance(col[0], DirectoryObject)
        self.assertNotIn("__odata_type", col[0].properties)

    def test_single_entity_keeps_class_type(self):
        ctx = ClientContext(test_site_url)
        payload = {"@odata.type": "#microsoft.graph.user", "id": "u1", "displayName": "Alice"}
        user = User(ctx)
        _graph_request().map_json(payload, user, V4JsonFormat())

        self.assertEqual(user.entity_type_name, "microsoft.graph.User")
        self.assertEqual(user.get_property("id"), "u1")
        self.assertNotIn("@odata.type", user.properties)
        self.assertNotIn("__odata_type", user.properties)

    def test_sharepoint_json_light_metadata_is_untouched(self):
        """JsonLight/SharePoint metadata must not leak into properties or type name."""
        ctx = ClientContext(test_site_url)
        payload = {"d": {"__metadata": {"type": "SP.Web"}, "Id": "web-1", "Url": "https://x"}}
        web = ctx.web
        ODataRequest(test_site_url, JsonLightFormat()).map_json(payload, web, JsonLightFormat())

        self.assertEqual(web.entity_type_name, "SP.Web")
        self.assertNotIn("__metadata", web.properties)


class TestQueryOptionsUrl(unittest.TestCase):
    """QueryOptions.to_url must prefix $ only for standard OData options."""

    def test_standard_options_keep_dollar_prefix(self):
        q = QueryOptions()
        q.select = ["displayName"]
        q.filter = "startswith(displayName,'A')"
        q.top = 10
        self.assertEqual(
            q.to_url(),
            "$select=displayName&$filter=startswith(displayName,'A')&$top=10",
        )

    def test_custom_params_are_verbatim(self):
        q = QueryOptions()
        q.custom["token"] = "latest"
        q.custom["$search"] = "pizza"
        q.custom["$count"] = "true"
        q.custom["$changeType"] = "created"
        self.assertEqual(q.to_url(), "token=latest&$search=pizza&$count=true&$changeType=created")


class TestDeltaToken(unittest.TestCase):
    """Delta requests must use ?token=... and expose a resumable token value."""

    def test_delta_url_uses_token_without_dollar(self):
        delta = GraphClient().me.drive.root.delta.token("abc123")
        self.assertEqual(
            ReadEntityQuery(delta).url,
            "https://graph.microsoft.com/v1.0/me/drive/root/delta?token=abc123",
        )

    def test_delta_token_parses_parenthesized_value(self):
        col = DeltaCollection(GraphClient(), DriveItem)
        col.set_property(
            "@odata.deltaLink",
            "https://graph.microsoft.com/v1.0/me/drive/root/delta?(token='MzslMjM0')",
        )
        self.assertEqual(col.delta_token, "MzslMjM0")

    def test_delta_token_parses_query_value(self):
        col = DeltaCollection(GraphClient(), DriveItem)
        col.set_property(
            "@odata.deltaLink",
            "https://graph.microsoft.com/v1.0/me/drive/root/delta?token=2021-09-29T20%3A00%3A00Z",
        )
        self.assertEqual(col.delta_token, "2021-09-29T20%3A00%3A00Z")

    def test_delta_token_parses_dollar_deltatoken(self):
        col = DeltaCollection(GraphClient(), DriveItem)
        col.set_property("@odata.deltaLink", "https://graph.microsoft.com/v1.0/users/delta?$deltatoken=latest")
        self.assertEqual(col.delta_token, "latest")

    def test_delta_resume_withholds_filter(self):
        delta = GraphClient().me.drive.root.delta
        delta.filter("startswith(name,'A')")
        with self.assertWarns(RuntimeWarning):
            delta.token("abc123")
        self.assertEqual(
            ReadEntityQuery(delta).url,
            "https://graph.microsoft.com/v1.0/me/drive/root/delta?token=abc123",
        )

    def test_delta_initial_request_keeps_filter(self):
        delta = GraphClient().me.drive.root.delta
        delta.filter("startswith(name,'A')")
        self.assertEqual(
            ReadEntityQuery(delta).url,
            "https://graph.microsoft.com/v1.0/me/drive/root/delta?$filter=startswith(name,'A')",
        )

    def test_delta_resume_warns_when_filter_present(self):
        delta = GraphClient().me.drive.root.delta
        delta.filter("startswith(name,'A')")
        with self.assertWarns(RuntimeWarning):
            delta.token("abc123")


class TestClientMetadata(unittest.TestCase):
    """Entity type-name resolution, query-option building and ClientResult wrapping."""

    def test_build_query_options(self):
        client = ClientContext(test_site_url)
        lib = client.web.default_document_library()
        options = ReadEntityQuery(lib, ["Author", "Comments"]).query_options
        self.assertEqual(str(options), "$select=Author,Comments&$expand=Author")

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

    def test_client_result_wraps_collection(self):
        client = ClientContext(test_site_url)
        result = ClientResult(client, StringCollection())
        self.assertIsInstance(result.value, StringCollection)


class _GuardResult:
    def __init__(self, value):
        self.value = value

    def execute_query(self):
        return self

    def __iter__(self):
        return iter(self.value)


def _make_sku(part_number):
    sku = mock.Mock()
    sku.sku_part_number = part_number
    return sku


class TestRequireLicense(unittest.TestCase):
    def _make_client(self) -> GraphClient:
        return GraphClient(tenant="contoso.onmicrosoft.com")

    def test_passes_when_sku_matches(self):
        client = self._make_client()
        collection = mock.Mock()
        collection.get.return_value = _GuardResult([_make_sku("BACKUP_STORAGE_ADDON"), _make_sku("ENTERPRISEPACK")])
        with mock.patch.object(GraphClient, "subscribed_skus", new_callable=mock.PropertyMock, return_value=collection):
            self.assertIs(client.require_license("BACKUP"), client)

    def test_exits_when_no_sku_matches(self):
        client = self._make_client()
        collection = mock.Mock()
        collection.get.return_value = _GuardResult([_make_sku("ENTERPRISEPACK")])
        with mock.patch.object(GraphClient, "subscribed_skus", new_callable=mock.PropertyMock, return_value=collection):
            with self.assertRaises(SystemExit):
                client.require_license("BACKUP")


class TestRequireDelegatedPermission(unittest.TestCase):
    def _make_client(self) -> GraphClient:
        ctx = GraphClient(tenant="contoso.onmicrosoft.com")
        ctx.pending_request().authentication_context._client_id = "app-id"
        return ctx

    def test_passes_when_scope_granted(self):
        client = self._make_client()
        client.get_delegated_permissions = mock.Mock(  # type: ignore[method-assign]
            return_value=_GuardResult(["User.Read", "Mail.Read"])
        )
        self.assertIs(client.require_delegated_permission("User.Read"), client)

    def test_exits_when_scope_missing(self):
        client = self._make_client()
        client.get_delegated_permissions = mock.Mock(  # type: ignore[method-assign]
            return_value=_GuardResult(["Mail.Read"])
        )
        with self.assertRaises(SystemExit):
            client.require_delegated_permission("User.Read")


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
