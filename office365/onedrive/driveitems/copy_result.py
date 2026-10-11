"""Waitable result of :meth:`~office365.onedrive.driveitems.driveItem.DriveItem.copy`.

``driveItem.copy`` is one of Microsoft Graph's long-running actions: the request
is accepted with ``202 Accepted`` and a ``Location`` header pointing at an
operation-status (monitor) URL. This module wraps that monitor URL in a
:class:`~office365.runtime.lro.LongRunningOperationResult` subclass whose
``wait_for_item`` / ``wait_for_item_async`` helpers poll to completion and return
the newly created ``DriveItem``.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, cast
from urllib.parse import unquote

from office365.runtime.lro import LongRunningOperationResult, OperationError, OperationStatus

if TYPE_CHECKING:
    from office365.graph_client import GraphClient
    from office365.onedrive.driveitems.driveItem import DriveItem
    from office365.runtime.client_runtime_context import ClientRuntimeContext

_DRIVES_ITEM_RE = re.compile(r"/drives/([^/]+)/items/([^/?]+)", re.IGNORECASE)


def _parse_drives_url(location: str | None) -> tuple[str | None, str | None]:
    """Return ``(drive_id, item_id)`` parsed from a ``/drives/{id}/items/{id}`` URL."""
    if not location:
        return None, None
    match = _DRIVES_ITEM_RE.search(location)
    if match is None:
        return None, None
    return unquote(match.group(1)), unquote(match.group(2))


def _response_body(status: OperationStatus) -> Any:
    """Best-effort JSON body of the terminal response (``None`` when not JSON)."""
    response = status.response
    if response is None:
        return None
    try:
        return response.json()
    except (ValueError, TypeError):
        return None


class DriveItemCopyResult(LongRunningOperationResult):
    """Result of :meth:`~office365.onedrive.driveitems.driveItem.DriveItem.copy`.

    The result value (and :attr:`monitor_url`) is the operation-status URL from
    the ``Location`` header; poll it with :meth:`wait` / :meth:`wait_async`, or
    use the convenience helpers below to get the copied item directly::

        result = source.copy(name="report (copy).xlsx", parent=destination).execute_query()
        copied = result.wait_for_item()  # blocking
        copied = await result.wait_for_item_async()  # non-blocking
    """

    def __init__(self, context: "ClientRuntimeContext", source: "DriveItem | None" = None) -> None:
        # The monitor URL lives on the drive's host (OneDrive / SharePoint), not
        # Graph, and is pre-authenticated for the original caller — attaching the
        # Graph token here would fail with "Invalid audience".
        super().__init__(context, str(), authenticate=False)
        self._source = source
        #: Destination drive id, captured from the parent reference when known.
        self.destination_drive_id: str | None = None

    def wait_for_item(
        self,
        *,
        interval: float = 5.0,
        timeout: float = 1800.0,
        on_progress: Any = None,
    ) -> "DriveItem":
        """Poll (blocking) until the copy completes, then return the new ``DriveItem``."""
        status = self.wait(interval=interval, timeout=timeout, on_progress=on_progress)
        return self._resolve_item(status)

    async def wait_for_item_async(
        self,
        *,
        interval: float = 5.0,
        timeout: float = 1800.0,
        on_progress: Any = None,
    ) -> "DriveItem":
        """Await the copy, then return the new ``DriveItem``."""
        status = await self.wait_async(interval=interval, timeout=timeout, on_progress=on_progress)
        return self._resolve_item(status)

    def _resolve_item(self, status: OperationStatus) -> "DriveItem":
        from office365.onedrive.driveitems.driveItem import DriveItem

        location_drive_id, location_item_id = _parse_drives_url(status.resource_location)
        drive_id = self.destination_drive_id or location_drive_id
        item_id = status.resource_id or location_item_id
        if drive_id and item_id:
            client = cast("GraphClient", self._context)
            item = client.drives[drive_id].items[item_id]
            item.get().execute_query()
            return item

        # Some OneDrive endpoints return the created item itself as the terminal
        # body (no ``resourceId``); deserialise it in place.
        body = _response_body(status)
        if isinstance(body, dict) and body.get("id"):
            item = DriveItem(self._context)
            for key, value in body.items():
                item.set_property(key, value, False)
            return item

        raise OperationError(
            "The copy completed but its result could not be resolved "
            f"(resourceId={status.resource_id!r}, resourceLocation={status.resource_location!r})."
        )
