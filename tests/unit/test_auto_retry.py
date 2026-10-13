"""Tests for the client-level retry policy (``with_auto_retry``)."""

from __future__ import annotations

import asyncio
import unittest
from unittest import mock

from office365.runtime.client_request_exception import ClientRequestException
from office365.sharepoint.client_context import ClientContext
from tests._scripted_transport import AsyncScriptedTransport as _AsyncScriptedTransport
from tests._scripted_transport import ScriptedTransport as _ScriptedTransport


def _context(payloads: list) -> ClientContext:
    ctx = ClientContext("https://contoso.sharepoint.com")
    ctx.pending_request().beforeExecute.clear()
    ctx.pending_request().transport = _ScriptedTransport(payloads)
    return ctx


def _async_context(payloads: list) -> ClientContext:
    ctx = ClientContext("https://contoso.sharepoint.com")
    ctx.pending_request().beforeExecute.clear()
    ctx.pending_request()._async_transport = _AsyncScriptedTransport(payloads)
    return ctx


class TestWithAutoRetry(unittest.TestCase):
    def test_configures_policy_and_chains(self):
        ctx = ClientContext("https://contoso.sharepoint.com")
        self.assertFalse(ctx.auto_retry)

        returned = ctx.with_auto_retry(max_retry=3)

        self.assertIs(returned, ctx)
        self.assertTrue(ctx.auto_retry)
        self.assertEqual(ctx.pending_request().retry_policy["max_retry"], 3)

    def test_clone_inherits_policy(self):
        ctx = ClientContext("https://contoso.sharepoint.com")
        ctx.with_auto_retry(max_retry=7)

        clone = ctx.clone("https://contoso.sharepoint.com/sites/team")

        self.assertTrue(clone.auto_retry)
        self.assertEqual(clone.pending_request().retry_policy["max_retry"], 7)

    def test_disabled_by_default(self):
        ctx = _context([{"status": 503}, {"d": {"Title": "Contoso"}}])

        with self.assertRaises(ClientRequestException):
            ctx.load(ctx.web).execute_query()

        self.assertEqual(ctx.pending_request().transport.calls, 1)

    def test_transient_failure_is_retried(self):
        ctx = _context([{"status": 503}, {"d": {"Title": "Contoso"}}])
        ctx.with_auto_retry(max_retry=3, timeout_secs=1, jitter=False)

        with mock.patch("office365.runtime.retry.sleep") as sleep_mock:
            ctx.load(ctx.web).execute_query()

        self.assertEqual(ctx.pending_request().transport.calls, 2)
        sleep_mock.assert_called_once_with(1)

    def test_permanent_failure_is_not_retried(self):
        ctx = _context([{"status": 400}])
        ctx.with_auto_retry(max_retry=3, timeout_secs=1, jitter=False)

        with mock.patch("office365.runtime.retry.sleep") as sleep_mock:
            with self.assertRaises(ClientRequestException):
                ctx.load(ctx.web).execute_query()

        self.assertEqual(ctx.pending_request().transport.calls, 1)
        sleep_mock.assert_not_called()

    def test_retries_exhausted_raise_last_error(self):
        ctx = _context([{"status": 503}, {"status": 503}, {"status": 503}])
        ctx.with_auto_retry(max_retry=2, timeout_secs=1, jitter=False)

        with mock.patch("office365.runtime.retry.sleep"):
            with self.assertRaises(ClientRequestException):
                ctx.load(ctx.web).execute_query()

        self.assertEqual(ctx.pending_request().transport.calls, 2)

    def test_async_transient_failure_is_retried(self):
        ctx = _async_context([{"status": 503}, {"d": {"Title": "Contoso"}}])
        ctx.with_auto_retry(max_retry=3, timeout_secs=1, jitter=False)

        async def _run() -> None:
            with mock.patch("office365.runtime.retry.asyncio.sleep", new=mock.AsyncMock()) as sleep_mock:
                await ctx.load(ctx.web).execute_query_async()
                sleep_mock.assert_awaited_once_with(1)

        asyncio.run(_run())

        self.assertEqual(ctx.pending_request().async_transport.calls, 2)

    def test_retry_does_not_recurse(self):
        """The retry loop must drive the queue once per attempt, not nest."""
        ctx = _context([{"status": 503}, {"status": 503}, {"d": {"Title": "Contoso"}}])
        ctx.with_auto_retry(max_retry=5, timeout_secs=0, jitter=False)

        with mock.patch("office365.runtime.retry.sleep"):
            ctx.load(ctx.web).execute_query()

        self.assertEqual(ctx.pending_request().transport.calls, 3)
        self.assertFalse(ctx._in_retry)


if __name__ == "__main__":
    unittest.main()
