"""Offline tests for permission hints on denied requests (Layer 2).

``@require_permission`` tags the query a builder method queues; when that request
is denied (HTTP 401/403) the raised
:class:`~office365.runtime.exceptions.AccessDeniedException` names the declared
permission (plus generic remediation), so callers see *what* to grant without
parsing docs. Non-permission failures are left untouched.
"""

from __future__ import annotations

import asyncio
import unittest

from office365.directory.permissions.require_permission import PermissionRequirement, require_permission
from office365.graph_client import GraphClient
from office365.runtime.exceptions import AccessDeniedException, ObjectNotFoundException
from office365.runtime.queries.client_query import ClientQuery
from tests._scripted_transport import AsyncScriptedTransport, ScriptedTransport


def _payload(status: int, code: str) -> dict:
    return {"status": status, "body": {"error": {"code": code, "message": "denied"}}}


def _client(status: int = 403, code: str = "accessDenied") -> GraphClient:
    client = GraphClient()
    client.pending_request().beforeExecute.clear()
    client.pending_request().transport = ScriptedTransport([_payload(status, code)])
    return client


class _AsyncBuilder:
    """Async builder used to check the decorator preserves awaitability."""

    def __init__(self, client: GraphClient) -> None:
        self.context = client

    @require_permission(application=["Baz.Read.All"])
    async def build(self) -> str:
        self.context.add_query(ClientQuery(self.context))
        return "done"


class TestPermissionRequirementHint(unittest.TestCase):
    def test_all_columns_and_notes(self):
        hint = PermissionRequirement(
            delegated=["Files.Read"],
            application=["Files.Read.All"],
            directory_roles=["Global Administrator"],
            notes="List drives",
        ).to_hint()
        self.assertIn("application Files.Read.All", hint)
        self.assertIn("delegated Files.Read", hint)
        self.assertIn("directory role Global Administrator", hint)
        self.assertIn("(List drives)", hint)


class TestRequirePermissionStampsQuery(unittest.TestCase):
    def test_async_decorated_method_stays_awaitable_and_stamps(self):
        client = GraphClient()
        builder = _AsyncBuilder(client)

        result = asyncio.run(builder.build())

        self.assertEqual(result, "done")
        self.assertEqual(client.last_query.permission_requirement.application, ["Baz.Read.All"])


class TestDeniedRequestHints(unittest.TestCase):
    def test_str_includes_guidance_and_declared_permission(self):
        client = _client()

        with self.assertRaises(AccessDeniedException) as raised:
            client.drives.get().execute_query()

        text = str(raised.exception)
        self.assertIn("require_application_permission", text)  # generic remediation
        self.assertIn("Files.Read.All", text)  # precise, from @require_permission

    def test_undecorated_denied_request_has_guidance_but_no_permission_hint(self):
        client = _client()

        with self.assertRaises(AccessDeniedException) as raised:
            client.me.get().execute_query()

        self.assertEqual(raised.exception.hints, ())
        self.assertIn("require_application_permission", str(raised.exception))

    def test_not_found_error_is_not_enriched(self):
        client = _client(404, "itemNotFound")

        with self.assertRaises(ObjectNotFoundException) as raised:
            client.drives.get().execute_query()

        self.assertEqual(raised.exception.hints, ())

    def test_async_denied_request_names_permission(self):
        client = GraphClient()
        client.pending_request().beforeExecute.clear()
        client.pending_request()._async_transport = AsyncScriptedTransport([_payload(403, "accessDenied")])

        async def _run() -> None:
            with self.assertRaises(AccessDeniedException) as raised:
                await client.drives.get().execute_query_async()
            self.assertIn("Files.Read.All", raised.exception.hints[0])

        asyncio.run(_run())


class TestHintApi(unittest.TestCase):
    def test_add_hint_is_chainable_and_listed(self):
        exc = AccessDeniedException(response=None)
        self.assertIs(exc.add_hint("grant X"), exc)
        self.assertEqual(exc.hints, ("grant X",))
        self.assertIn("grant X", str(exc))


if __name__ == "__main__":
    unittest.main()
