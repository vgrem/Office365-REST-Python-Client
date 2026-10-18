"""Calendar export adapters — a Graph calendar as a migration source, an ICS tree as the target.

Plug the core :class:`~office365.migration.job.MigrationJob` into Outlook calendar::

    from office365.migration import MigrationJob
    from office365.migration.outlook import CalendarExportOptions, CalendarSource, IcsExportTarget

    calendar = client.me.calendar.get().execute_query()
    job = MigrationJob(CalendarSource(calendar), IcsExportTarget("./calendar-export"))
    job.plan()
    job.run()
    print(job.verify().summary())

Export layout (the same convention the mail export uses)::

    <root>/<calendar>/<YYYY-MM-DD>_<subject-slug>_<id-digest>.ics   iCalendar document
    <root>/<calendar>/<same stem>.json                              sidecar record
    <root>/manifest.jsonl                                           one sidecar per line

One calendar per source: Graph exposes each calendar as its own event collection,
so a mailbox with several calendars is a job per calendar (or a loop), which also
keeps each export directory self-describing.

Three honest limits, all measured against Exchange:

* A recurring event is exported **once**, as its series master (``RRULE`` in the
  ``.ics``, ``recurrence`` in the sidecar); the individual occurrences are not
  separate items, because importing them would duplicate the series.
* Cancelled events are tombstones, skipped by default
  (``CalendarExportOptions.include_cancelled``): replaying one as a live meeting
  would be worse than losing the record of the cancellation.
* An ``.ics`` is a courtesy for other clients. Everything is also in the sidecar,
  which is what an import reads — iCalendar cannot carry Graph's recurrence object,
  the online-meeting provider, or the sensitivity/importance pair without loss.
"""

from __future__ import annotations

import hashlib
from typing import Any

from office365.migration.adapters import DataSource, MigrationProgress
from office365.migration.base import MigrationItem
from office365.migration.outlook.adapters import SidecarTreeTarget
from office365.migration.outlook.calendar_models import (
    EVENT_COLUMNS,
    STANDALONE_EVENT_TYPES,
    CalendarExportOptions,
    event_dest_path,
    event_envelope,
    event_ics,
    event_key,
)
from office365.migration.outlook.models import mail_slug
from office365.runtime.converters.scalars import iso_or_none
from office365.runtime.operations import emit_progress


def _md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


class CalendarSource(DataSource):
    """Enumerates one Graph calendar as one item per event.

    Each item carries its envelope in ``metadata``, so the export's index is written
    from the manifest itself — no second pass over the calendar.
    """

    def __init__(self, calendar, options: CalendarExportOptions | None = None) -> None:
        self._calendar = calendar
        self._options = options or CalendarExportOptions()
        self._events: dict[str, Any] = {}  # dest path -> event handle
        self._enumerated = False

    def label(self) -> str:
        name = self._options.root_name or getattr(self._calendar, "name", None) or self._calendar.id
        return f"calendar:{name}"

    def list_items(self, progress: MigrationProgress = None) -> list[MigrationItem]:
        root = self._options.root_name or mail_slug(getattr(self._calendar, "name", None)) or "calendar"
        display = getattr(self._calendar, "name", None) or root
        items: list[MigrationItem] = []
        for event in self._calendar.events.select(EVENT_COLUMNS).get_all().execute_query():
            kind = event.get_property("type")
            if not self._include(event, kind):
                continue
            item = self._item(event, root, display)
            self._events[item.dest_path] = event
            items.append(item)
            emit_progress(progress, done=len(items), stage="planning", items=[item])
        self._enumerated = True
        return items

    def _include(self, event, kind: str | None) -> bool:
        """Whether an event is exported on its own (a series master, not an instance)."""
        if event.get_property("isCancelled") and not self._options.include_cancelled:
            return False
        if kind in (None, *STANDALONE_EVENT_TYPES):
            return True
        return self._options.include_recurring_instances

    def _item(self, event, path: str, display: str) -> MigrationItem:
        dest = event_dest_path(event, path)
        return MigrationItem(
            source_path=dest,
            dest_path=dest,
            # An event has no byte size until its ``.ics`` is rendered; ``read()`` fills it.
            size_bytes=0,
            item_type="event",
            modified=iso_or_none(event.get_property("lastModifiedDateTime")),
            created=iso_or_none(event.get_property("createdDateTime")),
            source_id=event_key(event),
            metadata=event_envelope(event, path, self._options.extra_properties, display),
        )

    def _handle(self, item: MigrationItem):
        """The event for an item, enumerating once if the plan came from disk."""
        event = self._events.get(item.dest_path)
        if event is None and not self._enumerated:
            self.list_items()
            event = self._events.get(item.dest_path)
        if event is None:
            raise KeyError(f"{item.dest_path!r} was not enumerated by this source — re-plan the job")
        return event

    def read(self, item: MigrationItem) -> bytes:
        """The event's ``.ics`` document, rendered from the envelope in ``metadata``."""
        data = event_ics(item.metadata or {})
        item.size_bytes = len(data)
        return data

    def checksum(self, item: MigrationItem) -> str:
        return _md5(self.read(item))


class IcsExportTarget(SidecarTreeTarget):
    """Writes a portable ICS tree: one ``.ics`` plus one JSON sidecar per event."""

    content_suffix = ".ics"
    payload_key = "ics_path"


__all__ = ["CalendarSource", "IcsExportTarget"]
