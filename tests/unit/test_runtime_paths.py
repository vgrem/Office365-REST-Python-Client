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

    def test_build_nested_url_resource_path(self):
        parent_path = ResourcePath("root", ResourcePath("drive", self.client.me.resource_path))
        path = UrlPath("Sample.docx", UrlPath("2018", UrlPath("archive", parent_path)))
        self.assertEqual("/me/drive/root:/archive/2018/Sample.docx:/", str(path))

    def test_resolve_drive_url_path(self):
        parent_path = self.client.me.drive.root.resource_path
        assert parent_path is not None
        path = UrlPath("Sample.docx", UrlPath("2018", UrlPath("archive", parent_path)))
        item_id = uuid.uuid4().hex
        path.set_segment(item_id)
        self.assertEqual(f"/me/drive/items/{item_id}", str(path))

    def test_build_drive_children_path(self):
        item_id = uuid.uuid4().hex
        path = self.client.sites.root.drive.items[item_id].children.resource_path
        self.assertEqual(f"/sites/root/drive/items/{item_id}/children", str(path))

    def test_resolve_drive_children_path(self):
        """Setting a segment on ``root.children`` canonicalizes to /me/drive/items/{id}."""
        path = self.client.me.drive.root.children.resource_path
        assert path is not None
        item_id = uuid.uuid4().hex
        path.set_segment(item_id)
        self.assertEqual(f"/me/drive/items/{item_id}", str(path))

    def test_resolve_nested_drive_children_path(self):
        """A grandchild under a nested ``children`` keeps the canonical /items parents."""
        first_id = uuid.uuid4().hex
        grandchild_id = uuid.uuid4().hex
        nested_path = self.client.sites.root.drive.items[first_id].children.resource_path
        assert nested_path is not None
        nested_path.set_segment(grandchild_id)
        self.assertEqual(f"/sites/root/drive/items/{grandchild_id}", str(nested_path))

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

    def test_build_path_from_url(self):
        path_str = "/teams('7f919b9f-c220-4290-a4d8-5ff9300d1296')/operations('dc97f61a-0040-436f-ac09-427cd2456fd8')"
        path = ODataPathBuilder.parse_url(path_str)
        self.assertIsNotNone(path.segment)


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


def test_login_name_fallback_without_id():
    """Without an identifier, the login-name path is used as a fallback."""
    ctx = _ctx({"__metadata": {"type": "SP.User"}, "LoginName": _LOGIN})

    user = _ensure_user(ctx)

    assert "GetByName" in str(user.resource_path)


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


def test_odata_literal_escapes_single_quote_once():
    """A single quote is doubled exactly once in an OData string literal (#1052)."""
    assert ODataPathBuilder._encode_string("d'appello") == "'d''appello'"
    assert ODataPathBuilder._encode_string("it's 'x'") == "'it''s ''x'''"


def test_odata_literal_escapes_quote_in_file_path():
    ctx = ClientContext(test_site_url)
    path = "/sites/x/Shared Documents/d'appello.docx"

    resource_path = ctx.web.get_file_by_server_relative_path(path).resource_path

    assert "d''appello.docx" in str(resource_path)
    assert "''''" not in str(resource_path)


def test_odata_literal_encodes_special_chars_once():
    """Replacement text is not re-encoded: '%' becomes %25 and '+' stays %2B."""
    assert ODataPathBuilder._encode_string("50% + 1 & #2?*") == "'50%25 %2B 1 %26 %232%3F%2A'"


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


def test_file_exposes_move_by_path():
    ctx = ClientContext(test_site_url)
    file = ctx.web.get_file_by_server_relative_path("/sites/x/Shared Documents/a.xlsx")
    assert callable(file.move_by_path)


def test_alternate_key_path_renders_parenthesised_literal():
    from office365.runtime.paths.alternate_key import AlternateKeyPath

    path = AlternateKeyPath("uniqueName", "Group157", ResourcePath("groups"))

    assert str(path) == "/groups(uniqueName='Group157')"
    assert path.key_name == "uniqueName"
    assert path.delimiter is None


def test_appid_path_is_an_alternate_key_path():
    from office365.runtime.paths.alternate_key import AlternateKeyPath
    from office365.runtime.paths.appid import AppIdPath

    app_id = "00000000-0000-0000-0000-000000000000"
    path = AppIdPath(app_id, ResourcePath("servicePrincipals"))

    assert isinstance(path, AlternateKeyPath)
    assert path.key_name == "appId"
    assert str(path) == f"/servicePrincipals(appId='{app_id}')"


def test_get_by_alternate_key_builds_odata_path():
    client = GraphClient()

    group = client.groups.get_by_alternate_key("uniqueName", "Group157")

    assert str(group.resource_path) == "/groups(uniqueName='Group157')"


def test_get_by_app_id_delegates_to_alternate_key():
    client = GraphClient()
    app_id = "00000000-0000-0000-0000-000000000000"

    principal = client.service_principals.get_by_app_id(app_id)

    assert str(principal.resource_path) == f"/servicePrincipals(appId='{app_id}')"
