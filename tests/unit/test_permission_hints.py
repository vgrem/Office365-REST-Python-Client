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

from office365.graph_client import GraphClient
from office365.runtime.exceptions import AccessDeniedException, ObjectNotFoundException
from tests._scripted_transport import AsyncScriptedTransport, ScriptedTransport


def _payload(status: int, code: str) -> dict:
    return {"status": status, "body": {"error": {"code": code, "message": "denied"}}}


def _client(status: int = 403, code: str = "accessDenied") -> GraphClient:
    client = GraphClient()
    client.pending_request().beforeExecute.clear()
    client.pending_request().transport = ScriptedTransport([_payload(status, code)])
    return client


class TestDeniedRequestHints(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
