"""Merged unit tests (consolidated; see git history for originals)."""

from __future__ import annotations

import unittest
import uuid

from office365.graph_client import GraphClient
from office365.onedrive.internal.paths.url import UrlPath
from office365.runtime.paths.builder import ODataPathBuilder
from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.client_context import ClientContext
from tests import test_site_url
from tests._scripted_transport import RoutingTransport, ScriptedTransport


class TestGraphPathBuilding(unittest.TestCase):
    """Building and resolving Graph resource paths is a pure in-memory operation."""

    client = GraphClient()

    def test_resolve_drive_url_path(self):
        parent_path = self.client.me.drive.root.resource_path
        assert parent_path is not None
        path = UrlPath("Sample.docx", UrlPath("2018", UrlPath("archive", parent_path)))
        item_id = uuid.uuid4().hex
        path.set_segment(item_id)
        self.assertEqual(f"/me/drive/items/{item_id}", str(path))

    def test_recursive_children_requests_parent_collection(self):
        """Recursing into a child folder requests ``/items/{id}/children`` (not a bare id)."""
        transport = RoutingTransport(
            [
                ("/items/F1/children", {"value": [{"id": "F2", "name": "f2", "folder": {"childCount": 0}}]}),
                (
                    "/children",
                    {"value": [{"id": "F1", "name": "f1", "folder": {"childCount": 1}}]},
                ),
            ]
        )
        client = GraphClient()
        client.pending_request().beforeExecute.clear()
        client.pending_request().transport = transport

        client.me.drive.root.get_folders(recursive=True).execute_query()

        assert "/me/drive/root/children" in transport.calls[0]
        assert any("/me/drive/items/F1/children" in url for url in transport.calls), transport.calls

    def test_resolve_term_children_path(self):
        group_id = uuid.uuid4().hex
        set_id = uuid.uuid4().hex
        term_id = uuid.uuid4().hex
        path = self.client.sites.root.term_store.groups[group_id].sets[set_id].children.resource_path
        assert path is not None
        path = path.set_segment(term_id)
        self.assertEqual(
            f"/sites/root/termStore/groups/{group_id}/sets/{set_id}/terms/{term_id}",
            str(path),
        )


_LOGIN = "i:0#.f|membership|user.name@domain.com"


def _ctx(payload: dict) -> ClientContext:
    ctx = ClientContext(test_site_url)
    ctx.pending_request().beforeExecute.clear()
    ctx.pending_request().transport = ScriptedTransport([{"d": payload}])
    return ctx


def _ensure_user(ctx: ClientContext):
    return ctx.web.ensure_user(_LOGIN).execute_query()


def test_id_takes_precedence_when_mapped():
    """An identifier wins: the principal is addressed by Id, not by login name."""
    ctx = _ctx({"__metadata": {"type": "SP.User"}, "Id": 6, "LoginName": _LOGIN})

    user = _ensure_user(ctx)

    assert "siteUsers(6)" in str(user.resource_path)
    assert "GetByName" not in str(user.resource_path)
    assert user.id == 6  # noqa: PLR2004
    assert user.login_name == _LOGIN


def test_entity_method_path_is_not_clobbered_by_id():
    """A pre-existing service-operation path (GetByTitle) must survive an Id mapping."""
    ctx = ClientContext(test_site_url)
    lst = ctx.web.lists.get_by_title("X")

    lst.set_property("Id", 6)

    assert "GetByTitle" in str(lst.resource_path)


class _PathCaptureTransport(ScriptedTransport):
    def __init__(self, payloads):
        super().__init__(payloads)
        self.requests = []

    def execute(self, request):
        self.requests.append(request)
        return super().execute(request)


def test_odata_literal_keeps_slashes():
    """Slashes stay literal in OData string literals (no %2F URL inflation)."""
    ctx = ClientContext(test_site_url)
    path = "/sites/x/Shared Documents/deep/nested/folder/report.xlsx"

    resource_path = ctx.web.get_file_by_server_relative_path(path).resource_path

    assert "%2F" not in str(resource_path)
    assert path in str(resource_path)


def test_odata_function_datetime_argument_uses_datetime_literal():
    """A datetime function argument becomes an OData v3 ``datetime'...'`` literal.

    Before this branch a ``datetime`` fell through to ``quote(str(value))``, which
    produced an invalid path (e.g. for ``TimeZone.UTCToLocalTime``).
    """
    from datetime import date, datetime, timezone

    assert ODataPathBuilder._encode_odata_value(datetime(2021, 6, 1, 15, 0, 0)) == "datetime'2021-06-01T15:00:00'"
    assert (
        ODataPathBuilder._encode_odata_value(datetime(2021, 6, 1, 15, 0, 0, tzinfo=timezone.utc))
        == "datetime'2021-06-01T15:00:00'"
    )
    assert ODataPathBuilder._encode_odata_value(date(2021, 6, 1)) == "date'2021-06-01'"


def test_move_file_by_path_sends_paths_in_body():
    """MoveCopyUtil.MoveFileByPath carries both paths in the request body, not the URL."""
    from office365.sharepoint.utilities.move_copy_options import MoveCopyOptions
    from office365.sharepoint.utilities.move_copy_util import MoveCopyUtil

    src = "/sites/x/Shared Documents/deep/nested/folder/a.xlsx"
    dest = "/sites/x/Shared Documents/deep/nested/archive/a.xlsx"
    transport = _PathCaptureTransport([{}])
    ctx = ClientContext(test_site_url)
    ctx.pending_request().beforeExecute.clear()
    ctx.pending_request().transport = transport

    MoveCopyUtil.move_file_by_path(ctx, src, dest, MoveCopyOptions(KeepBoth=False))
    ctx.execute_query()

    assert len(transport.requests) == 1
    request = transport.requests[0]
    assert "MoveFileByPath" in request.url
    assert "%2F" not in request.url
    assert request.data["srcPath"]["DecodedUrl"].endswith(src)
    assert request.data["destPath"]["DecodedUrl"].endswith(dest)


def test_appid_path_is_an_alternate_key_path():
    from office365.runtime.paths.alternate_key import AlternateKeyPath
    from office365.runtime.paths.appid import AppIdPath

    app_id = "00000000-0000-0000-0000-000000000000"
    path = AppIdPath(app_id, ResourcePath("servicePrincipals"))

    assert isinstance(path, AlternateKeyPath)
    assert path.key_name == "appId"
    assert str(path) == f"/servicePrincipals(appId='{app_id}')"


def test_get_by_app_id_delegates_to_alternate_key():
    client = GraphClient()
    app_id = "00000000-0000-0000-0000-000000000000"

    principal = client.service_principals.get_by_app_id(app_id)

    assert str(principal.resource_path) == f"/servicePrincipals(appId='{app_id}')"
