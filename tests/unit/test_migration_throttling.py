"""Tests for the migration throttling monitor (offline)."""

from __future__ import annotations

import asyncio
import json
import logging
import threading
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime

import pytest
from office365.migration import MigrationSession, ThrottleMonitor
from office365.migration.adapters.filesystem import FileSystemSource, FileSystemTarget
from office365.migration.job import MigrationJob
from office365.migration.logging import LOGGER_NAME
from office365.migration.throttling import _CountingTransport
from office365.runtime.transport.base import BaseTransport

THROTTLE_AFTER = 10
OTHER_THROTTLE_AFTER = 5
PAUSE_SECONDS = 2
SERVICE_UNAVAILABLE = 503
TOO_MANY_REQUESTS = 429


class _Response:
    """The slice of a response the monitor reads."""

    def __init__(self, status_code=None, headers=None):
        self.status_code = status_code
        self.headers = headers or {}


class _Transport(BaseTransport):
    """A transport that returns a pre-set response (sync and async)."""

    def __init__(self, response):
        self.response = response
        self.calls = 0

    def execute(self, request):
        self.calls += 1
        return self.response

    async def execute_async(self, request):
        self.calls += 1
        return self.response


class _Request:
    """The slice of a pending request the monitor attaches to."""

    def __init__(self, transport, async_transport=None):
        self.transport = transport
        self._async_transport = async_transport

    @property
    def has_async_transport(self):
        return self._async_transport is not None

    @property
    def async_transport(self):
        return self._async_transport or self.transport

    def with_async_transport(self, transport):
        self._async_transport = transport
        return self


class _Context:
    def __init__(self, request):
        self._request = request

    def pending_request(self):
        return self._request


class _Capture(logging.Handler):
    def __init__(self):
        super().__init__()
        self.records = []

    def emit(self, record):
        self.records.append(record)


@pytest.fixture
def capture():
    handler = _Capture()
    logger = logging.getLogger(LOGGER_NAME)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    yield handler
    logger.removeHandler(handler)


def _events(handler, name):
    return [record for record in handler.records if getattr(record, "event", None) == name]


# ── counting ─────────────────────────────────────────────────────


def test_a_throttled_response_is_counted_with_its_retry_after():
    monitor = ThrottleMonitor()
    responses = [
        _Response(TOO_MANY_REQUESTS, {"Retry-After": str(THROTTLE_AFTER)}),
        _Response(TOO_MANY_REQUESTS, {"Retry-After": str(OTHER_THROTTLE_AFTER)}),
        _Response(SERVICE_UNAVAILABLE),
    ]

    for response in responses:
        monitor.observe(response)

    assert monitor.responses == len(responses)
    assert monitor.throttled == len(responses)
    assert monitor.retry_after == THROTTLE_AFTER + OTHER_THROTTLE_AFTER


def test_an_ordinary_or_client_error_response_is_not_a_throttle():
    monitor = ThrottleMonitor()
    responses = [None, _Response(), _Response(200), _Response(404), _Response(500)]

    for response in responses:
        monitor.observe(response)

    assert monitor.responses == len(responses)
    assert monitor.throttled == 0
    assert monitor.summary() == ""


def test_an_http_date_retry_after_is_parsed():
    monitor = ThrottleMonitor()
    when = datetime.now(timezone.utc) + timedelta(seconds=THROTTLE_AFTER)
    monitor.observe(_Response(SERVICE_UNAVAILABLE, {"Retry-After": format_datetime(when, usegmt=True)}))

    assert THROTTLE_AFTER - 1 <= monitor.retry_after <= THROTTLE_AFTER + 1


def test_counting_is_thread_safe():
    monitor = ThrottleMonitor()
    response = _Response(TOO_MANY_REQUESTS, {"Retry-After": "1"})
    workers, per_worker = 8, 50

    def _hammer():
        for _ in range(per_worker):
            monitor.observe(response)

    threads = [threading.Thread(target=_hammer) for _ in range(workers)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert monitor.responses == workers * per_worker
    assert monitor.throttled == workers * per_worker
    assert monitor.retry_after == workers * per_worker


# ── reading ──────────────────────────────────────────────────────


def test_the_summary_names_the_codes_and_the_cost():
    monitor = ThrottleMonitor()
    monitor.observe(_Response(200))
    monitor.observe(_Response(TOO_MANY_REQUESTS, {"Retry-After": "2"}))
    monitor.observe(_Response(SERVICE_UNAVAILABLE, {"Retry-After": "3"}))

    assert monitor.summary() == "throttled 2/3 response(s) (429: 1, 503: 1), 5s of Retry-After"


def test_the_snapshot_is_json_serializable_with_stable_keys():
    monitor = ThrottleMonitor()
    monitor.observe(_Response(TOO_MANY_REQUESTS, {"Retry-After": "4"}))

    payload = monitor.snapshot()

    assert payload == {
        "responses": 1,
        "throttled": 1,
        "retry_after_s": 4.0,
        "by_status": {"429": 1},
    }
    assert monitor.to_dict() == payload
    assert json.loads(json.dumps(payload)) == payload


def test_reset_clears_the_counters():
    monitor = ThrottleMonitor()
    monitor.observe(_Response(TOO_MANY_REQUESTS))

    monitor.reset()

    assert monitor.snapshot() == {
        "responses": 0,
        "throttled": 0,
        "retry_after_s": 0.0,
        "by_status": {},
    }


# ── wiring ───────────────────────────────────────────────────────


def test_attach_counts_the_responses_a_transport_returns():
    inner = _Transport(_Response(TOO_MANY_REQUESTS, {"Retry-After": "7"}))
    context = _Context(_Request(inner))

    monitor = ThrottleMonitor().attach(context)
    wrapped = context.pending_request().transport
    response = wrapped.execute(object())

    assert isinstance(wrapped, _CountingTransport)
    assert wrapped.inner is inner
    assert wrapped.monitor is monitor
    assert response.status_code == TOO_MANY_REQUESTS
    assert inner.calls == 1
    assert monitor.throttled == 1


def test_attach_counts_the_async_path_too():
    inner = _Transport(_Response(SERVICE_UNAVAILABLE))
    dedicated = _Transport(_Response(TOO_MANY_REQUESTS))
    context = _Context(_Request(inner, dedicated))

    ThrottleMonitor().attach(context)
    wrapped = context.pending_request().async_transport

    async def _run():
        return await wrapped.execute_async(object())

    asyncio.run(_run())

    assert context.pending_request().transport.inner is inner
    assert context.pending_request().transport.monitor.throttled == 1


def test_attaching_twice_does_not_stack_wrappers():
    inner = _Transport(_Response(200))
    context = _Context(_Request(inner))
    monitor = ThrottleMonitor()

    monitor.attach(context)
    monitor.attach(context)

    wrapped = context.pending_request().transport
    assert isinstance(wrapped, _CountingTransport)
    assert wrapped.inner is inner


# ── the session reports it ───────────────────────────────────────


def _session(tmp_path, monitor=None):
    session = MigrationSession(throttle=monitor).register()
    source = tmp_path / "src"
    source.mkdir()
    (source / "a.txt").write_text("a", encoding="utf-8")
    session.add_task(FileSystemSource(source), FileSystemTarget(tmp_path / "out"))
    return session


def test_a_session_reports_throttling_as_an_event_and_a_total(tmp_path, capture, monkeypatch):
    monitor = ThrottleMonitor()

    observed = [
        _Response(TOO_MANY_REQUESTS, {"Retry-After": str(PAUSE_SECONDS)}),
        _Response(SERVICE_UNAVAILABLE),
    ]

    def _run(_self, progress=None):
        for response in observed:
            monitor.observe(response)

    monkeypatch.setattr(MigrationJob, "run", _run)
    session = _session(tmp_path, monitor)

    session.start()

    throttled = _events(capture, "throttled")
    assert len(throttled) == 1
    assert throttled[0].throttled == len(observed)  # type: ignore[attr-defined]
    assert throttled[0].responses == len(observed)  # type: ignore[attr-defined]
    assert throttled[0].retry_after_s == float(PAUSE_SECONDS)  # type: ignore[attr-defined]
    assert throttled[0].getMessage() == ("throttled 2/2 response(s) (429: 1, 503: 1), 2s of Retry-After")
    completed = _events(capture, "run.completed")[0]
    assert completed.throttled == len(observed)  # type: ignore[attr-defined]
    assert completed.by_status == {"429": 1, "503": 1}  # type: ignore[attr-defined]


def test_a_session_without_a_monitor_adds_no_throttling_fields(tmp_path, capture):
    session = _session(tmp_path)

    session.start()

    completed = _events(capture, "run.completed")[0]
    assert not hasattr(completed, "throttled")
    assert not hasattr(completed, "responses")
    assert session.throttle is None


def test_a_run_that_is_not_throttled_emits_no_event(tmp_path, capture):
    session = _session(tmp_path, ThrottleMonitor())

    session.start()

    assert _events(capture, "throttled") == []
    assert _events(capture, "run.completed")[0].throttled == 0  # type: ignore[attr-defined]
