"""Offline tests for the dedicated async offload executor.

The async twins offload blocking transport work (and ``beforeExecute`` hooks)
to a worker pool owned by the library instead of the event loop's shared default
executor, so an app can size HTTP concurrency independently and heavy requests
cannot starve other loop callbacks. These tests cover the lazy singleton
lifecycle, the configure/shutdown API and the per-transport override.
"""

from __future__ import annotations

import asyncio
import contextvars
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.transport import offload
from office365.runtime.transport.base import BaseTransport
from office365.runtime.transport.offload import (
    configure_offload_executor,
    get_offload_executor,
    run_offloaded,
    shutdown_offload_executor,
)
from tests._scripted_transport import build_response

_URL = "https://contoso.example.com/_api/web"
_SHARED_PREFIX = "office365-offload"

#: Context variable used to prove propagation/isolations across the thread hop.
_REQUEST_ID: contextvars.ContextVar[str | None] = contextvars.ContextVar("request_id", default=None)


@pytest.fixture(autouse=True)
def _reset_offload_executor():
    """Isolate the process-wide pool: start from and leave a clean slate."""
    shutdown_offload_executor(wait=True)
    yield
    shutdown_offload_executor(wait=True)


class _ThreadNameTransport(BaseTransport):
    """Records the name of the worker thread that runs ``execute``."""

    def __init__(self) -> None:
        self.thread_names: list[str] = []

    def execute(self, request: RequestOptions):
        self.thread_names.append(threading.current_thread().name)
        return build_response(request, b"{}")


def test_get_offload_executor_is_lazy_singleton() -> None:
    assert offload._pool._executor is None  # no pool before the first async request

    first = get_offload_executor()

    assert get_offload_executor() is first
    assert offload._pool._executor is first


def test_stream_async_uses_shared_pool() -> None:
    transport = _ThreadNameTransport()

    async def _drain() -> bytes:
        request = RequestOptions(url=_URL)
        return b"".join([chunk async for chunk in transport.stream_async(request, chunk_size=4)])

    assert asyncio.run(_drain()) == b"{}"
    assert transport.thread_names
    assert transport.thread_names[0].startswith(_SHARED_PREFIX)


def test_transport_offload_executor_override() -> None:
    transport = _ThreadNameTransport()
    with ThreadPoolExecutor(max_workers=1, thread_name_prefix="custom-pool") as pool:
        transport.offload_executor = pool
        asyncio.run(transport.execute_async(RequestOptions(url=_URL)))

    assert transport.thread_names == ["custom-pool_0"]


def test_configure_after_creation_raises() -> None:
    get_offload_executor()

    with pytest.raises(RuntimeError):
        configure_offload_executor(max_workers=2)


def test_configure_rejects_invalid_max_workers() -> None:
    with pytest.raises(ValueError):
        configure_offload_executor(max_workers=0)


def test_shutdown_drops_pool_and_restores_defaults() -> None:
    configure_offload_executor(max_workers=1, thread_name_prefix="first")
    first = get_offload_executor()

    shutdown_offload_executor(wait=True)

    assert offload._pool._executor is None
    second = get_offload_executor()
    assert second is not first

    transport = _ThreadNameTransport()
    asyncio.run(transport.execute_async(RequestOptions(url=_URL)))
    assert transport.thread_names[0].startswith(_SHARED_PREFIX)


def test_run_offloaded_uses_given_executor() -> None:
    def _thread_name() -> str:
        return threading.current_thread().name

    with ThreadPoolExecutor(max_workers=1, thread_name_prefix="ctx-pool") as pool:
        assert asyncio.run(run_offloaded(_thread_name, executor=pool)) == "ctx-pool_0"
