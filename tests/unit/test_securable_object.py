"""Offline tests for ``Web.get_securable_object`` and the ``grant_access``/``revoke_access`` wrappers.

``get_securable_object`` is a pure address builder (deferred, no request), so the
bulk of these tests assert the resource path it produces. The permission helpers
are checked by driving a scripted transport and inspecting the request sent.
"""

from __future__ import annotations

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.listitem import ListItem
from office365.sharepoint.permissions.roles.definitions.definition import RoleDefinition
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


# --- SecurableObject.grant_access / revoke_access -----------------------------


def _loaded_principal(ctx) -> User:
    principal = User(ctx)
    principal.set_property("Id", PRINCIPAL_ID)
    return principal


def _loaded_role(ctx) -> RoleDefinition:
    role = RoleDefinition(ctx)
    role.set_property("Id", ROLE_DEF_ID)
    return role


def test_grant_access_is_deferred():
    ctx = _ctx()
    ctx.pending_request().beforeExecute.clear()
    transport = _CaptureTransport([])
    ctx.pending_request().transport = transport
    target = ctx.web.get_securable_object("web")

    target.grant_access(_loaded_principal(ctx), _loaded_role(ctx))

    assert transport.calls == 0
    assert transport.requests == []
