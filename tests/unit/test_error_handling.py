"""Offline tests for error dispatch in :class:`~office365.runtime.client_request.ClientRequest`.

A failure is swallowed only when a registered ``on_error`` handler's condition
matches. Before the fix, registering *any* handler made every later failure on
the request silent — so a scoped handler left behind by a completed query hid
unrelated errors (e.g. a rejected content-type field link).
"""

from __future__ import annotations

import pytest
from office365.runtime.exceptions import ObjectNotFoundException
from office365.sharepoint.client_context import ClientContext
from tests import test_site_url
from tests._scripted_transport import ScriptedTransport

_NOT_FOUND = {
    "http_status": 404,
    "body": {"error": {"code": "Request_ResourceNotFound", "message": "Resource not found"}},
}

_OK = {"d": {"Title": "Site"}}


def _sp(payloads):
    ctx = ClientContext(test_site_url)
    ctx.pending_request().beforeExecute.clear()
    ctx.pending_request().transport = ScriptedTransport(payloads)
    return ctx


def test_scoped_handler_left_by_finished_query_does_not_swallow_later_failure():
    # q1 succeeds; the handler registered for it stays on the request. q2 then
    # fails and must propagate because that stale handler no longer matches.
    ctx = _sp([_OK, _NOT_FOUND])
    ctx.web.get()
    ctx.on_error(lambda _e: None)  # scoped to q1
    ctx.web.get()  # q2

    with pytest.raises(ObjectNotFoundException):
        ctx.execute_query()


def test_handler_once_is_removed_after_match():
    ctx = _sp([_NOT_FOUND, _NOT_FOUND])
    handled = []
    ctx.pending_request().on_error(handled.append, once=True, condition=lambda: True)

    ctx.web.get().execute_query()
    with pytest.raises(ObjectNotFoundException):
        ctx.web.get().execute_query()

    assert len(handled) == 1
