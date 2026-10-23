"""Tests for the client-level retry policy (``with_auto_retry``)."""

from __future__ import annotations

import unittest
from unittest import mock

from office365.runtime.client_request_exception import ClientRequestException
from office365.sharepoint.client_context import ClientContext
from tests._scripted_transport import ScriptedTransport as _ScriptedTransport


def _context(payloads: list) -> ClientContext:
    ctx = ClientContext("https://contoso.sharepoint.com")
    ctx.pending_request().beforeExecute.clear()
    ctx.pending_request().transport = _ScriptedTransport(payloads)
    return ctx


class TestWithAutoRetry(unittest.TestCase):
    def test_permanent_failure_is_not_retried(self):
        ctx = _context([{"status": 400}])
        ctx.with_auto_retry(max_retry=3, timeout_secs=1, jitter=False)

        with mock.patch("office365.runtime.retry.sleep") as sleep_mock:
            with self.assertRaises(ClientRequestException):
                ctx.load(ctx.web).execute_query()

        self.assertEqual(ctx.pending_request().transport.calls, 1)
        sleep_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
