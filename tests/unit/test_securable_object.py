"""Offline tests for ``Web.get_securable_object`` and the ``grant_access``/``revoke_access`` wrappers.

``get_securable_object`` is a pure address builder (deferred, no request), so the
bulk of these tests assert the resource path it produces. The permission helpers
are checked by driving a scripted transport and inspecting the request sent.
"""

from __future__ import annotations

import pytest
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.listitem import ListItem
from office365.sharepoint.lists.list import List
from office365.sharepoint.permissions.roles.definitions.definition import RoleDefinition
from office365.sharepoint.permissions.securable_object import SecurableObject
from office365.sharepoint.principal.users.user import User
from tests import test_site_url
from tests._scripted_transport import ScriptedTransport


class _CaptureTransport(ScriptedTransport):
    def __init__(self, payloads):
        super().__init__(payloads)
        self.requests = []

    def execute(self, request):
        self.requests.append(request)
        return super().execute(request)


PRINCIPAL_ID = 6
ROLE_DEF_ID = 1073741827


def _ctx() -> ClientContext:
    return ClientContext(test_site_url)


# --- Web.get_securable_object -------------------------------------------------


def test_scope_is_case_insensitive():
    ctx = _ctx()

    assert ctx.web.get_securable_object("WEB") is ctx.web
    assert isinstance(ctx.web.get_securable_object("Folder", url="/sites/x/f"), ListItem)


def test_scope_list_returns_list_addressed_by_title():
    ctx = _ctx()

    target = ctx.web.get_securable_object("list", list_title="Documents")

    assert isinstance(target, List)
    assert isinstance(target, SecurableObject)
    assert "GetByTitle" in str(target.resource_path)
    assert "Documents" in str(target.resource_path)


def test_scope_folder_returns_the_folders_list_item():
    ctx = _ctx()
    path = "/sites/x/Shared Documents/sub"

    target = ctx.web.get_securable_object("folder", url=path)

    assert isinstance(target, ListItem)
    resource_path = str(target.resource_path)
    assert "getFolderByServerRelativePath" in resource_path
    assert "ListItemAllFields" in resource_path
    assert path in resource_path


@pytest.mark.parametrize("scope", ["item", "file"])
def test_scope_item_and_file_return_the_files_list_item(scope):
    ctx = _ctx()
    path = "/sites/x/Shared Documents/report.docx"

    target = ctx.web.get_securable_object(scope, url=path)

    assert isinstance(target, ListItem)
    resource_path = str(target.resource_path)
    assert "getFileByServerRelativePath" in resource_path
    assert "listItemAllFields" in resource_path
    assert path in resource_path


# --- SecurableObject.grant_access / revoke_access -----------------------------


def _grant_ctx(payloads):
    ctx = _ctx()
    ctx.pending_request().beforeExecute.clear()
    transport = _CaptureTransport(payloads)
    ctx.pending_request().transport = transport
    return ctx, transport


def _loaded_principal(ctx) -> User:
    principal = User(ctx)
    principal.set_property("Id", PRINCIPAL_ID)
    return principal


def _loaded_role(ctx) -> RoleDefinition:
    role = RoleDefinition(ctx)
    role.set_property("Id", ROLE_DEF_ID)
    return role


def test_grant_access_queues_add_role_assignment():
    ctx, transport = _grant_ctx([{}])
    target = ctx.web.get_securable_object("list", list_title="Documents")

    result = target.grant_access(_loaded_principal(ctx), _loaded_role(ctx)).execute_query()

    assert result is target
    assert len(transport.requests) == 1
    request = transport.requests[0]
    assert "AddRoleAssignment" in request.url
    assert f"principalId={PRINCIPAL_ID}" in request.url
    assert f"roleDefId={ROLE_DEF_ID}" in request.url


def test_revoke_access_queues_remove_role_assignment():
    ctx, transport = _grant_ctx([{}])
    target = ctx.web.get_securable_object("list", list_title="Documents")

    result = target.revoke_access(_loaded_principal(ctx), _loaded_role(ctx)).execute_query()

    assert result is target
    assert len(transport.requests) == 1
    assert "RemoveRoleAssignment" in transport.requests[0].url


def test_grant_access_is_deferred():
    ctx = _ctx()
    ctx.pending_request().beforeExecute.clear()
    transport = _CaptureTransport([])
    ctx.pending_request().transport = transport
    target = ctx.web.get_securable_object("web")

    target.grant_access(_loaded_principal(ctx), _loaded_role(ctx))

    assert transport.calls == 0
    assert transport.requests == []
