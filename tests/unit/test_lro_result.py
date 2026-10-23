"""Offline tests for Graph long-running-operation wiring.

Covers the two Phase 7 pieces layered on the generic
:mod:`office365.runtime.lro` poller:

- :class:`~office365.runtime.lro.LongRunningOperationResult`, the monitor-URL
  result returned by Graph long-running actions, and
- :class:`~office365.onedrive.driveitems.copy_result.DriveItemCopyResult`, which
  turns a completed ``driveItem.copy`` into the freshly created item.
"""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import Any

import pytest
from office365.graph_client import GraphClient
from office365.onedrive.driveitems.copy_result import DriveItemCopyResult
from office365.onedrive.listitems.item_reference import ItemReference
from office365.runtime.lro import LongRunningOperationResult
from tests._scripted_transport import AsyncScriptedTransport, ScriptedTransport, build_response

_MONITOR = "https://graph.microsoft.com/monitor/abc"


def _lro(http_status: int, body: Any = None, headers: dict[str, str] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"http_status": http_status}
    if body is not None:
        payload["body"] = body
    if headers is not None:
        payload["headers"] = headers
    return payload


def _graph_client(
    *,
    sync_payloads: list[Any] | None = None,
    async_payloads: list[Any] | None = None,
) -> GraphClient:
    client = GraphClient()
    client.pending_request().beforeExecute.clear()
    if sync_payloads is not None:
        client.pending_request().transport = ScriptedTransport(list(sync_payloads))
    if async_payloads is not None:
        client.pending_request()._async_transport = AsyncScriptedTransport(list(async_payloads))
    return client


# -- LongRunningOperationResult --------------------------------------------


def test_long_running_result_wait_async():
    client = _graph_client(
        async_payloads=[
            _lro(202, {"status": "inProgress"}, {"Retry-After": "0"}),
            _lro(202, {"status": "completed", "resourceId": "9"}),
        ]
    )
    result = LongRunningOperationResult(client, _MONITOR)
    status = asyncio.run(result.wait_async())
    assert status.is_success
    assert result.resource_id == "9"


def test_long_running_result_streams_snapshots():
    client = _graph_client(
        sync_payloads=[
            _lro(202, {"status": "inProgress", "percentageComplete": 12}, {"Retry-After": "0"}),
            _lro(202, {"status": "completed", "resourceId": "42"}),
        ]
    )
    result = LongRunningOperationResult(client, _MONITOR)
    seen = [status.status for status in result.stream()]
    assert seen == ["inProgress", "completed"]
    # A stream keeps the result's view current, so `cancel()` and the resource
    # properties work the same as after `wait()`.
    assert result.last_status is not None
    assert result.last_status.is_success
    assert result.resource_id == "42"


def test_long_running_result_astream():
    client = _graph_client(
        async_payloads=[
            _lro(202, {"status": "inProgress"}, {"Retry-After": "0"}),
            _lro(202, {"status": "completed", "resourceId": "9"}),
        ]
    )
    result = LongRunningOperationResult(client, _MONITOR)

    async def collect() -> list[str | None]:
        return [status.status async for status in result.astream()]

    assert asyncio.run(collect()) == ["inProgress", "completed"]
    assert result.resource_id == "9"


def test_completed_result_is_terminal_without_a_monitor():
    response = build_response(SimpleNamespace(url=_MONITOR), {"http_status": 200, "body": {"id": "1"}})
    result = LongRunningOperationResult.completed(_graph_client(), response)
    assert result.is_completed
    assert result.monitor_url is None
    assert result.last_status is not None
    assert result.last_status.status == "completed"
    # No poll is attempted, so a result without a monitor URL is still waitable.
    assert result.wait() is result.last_status
    assert [s.status for s in result.stream()] == ["completed"]
    assert asyncio.run(result.wait_async()) is result.last_status
    with pytest.raises(ValueError, match="monitor URL"):
        result.to_poller()


# -- DriveItemCopyResult ----------------------------------------------------


def test_copy_result_resolves_item_from_resource_location():
    client = _graph_client(
        sync_payloads=[
            _lro(
                202,
                {
                    "status": "completed",
                    "resourceId": "01ITEM",
                    "resourceLocation": "https://graph.microsoft.com/v1.0/drives/drive1/items/01ITEM",
                },
            ),
            {"id": "01ITEM", "name": "report (copy).xlsx"},
        ]
    )
    result = DriveItemCopyResult(client, None)
    result.set_property("__value", _MONITOR)
    item = result.wait_for_item()
    assert item.id == "01ITEM"
    assert item.name == "report (copy).xlsx"


def test_copy_result_falls_back_to_body_item():
    client = _graph_client(sync_payloads=[_lro(200, {"id": "01ITEM", "name": "copy.xlsx"})])
    result = DriveItemCopyResult(client, None)
    result.set_property("__value", _MONITOR)
    item = result.wait_for_item()
    assert item.id == "01ITEM"
    assert item.name == "copy.xlsx"


def test_drive_item_copy_returns_waitable_result():
    client = _graph_client(sync_payloads=[_lro(202, headers={"Location": "https://graph.microsoft.com/monitor/xyz"})])
    source = client.drives["d1"].items["src"]
    result = source.copy(name="copy.xlsx", parent=ItemReference(driveId="d1", id="dest"))
    assert isinstance(result, DriveItemCopyResult)
    result.execute_query()
    assert result.monitor_url == "https://graph.microsoft.com/monitor/xyz"
    assert result.destination_drive_id == "d1"
