"""Calendar adapters — a Graph calendar as a source, an ICS tree as a target, and back.

Export a calendar::

    from office365.migration import MigrationJob
    from office365.migration.outlook import CalendarExportOptions, CalendarSource, IcsExportTarget

    calendar = client.me.calendar.get().execute_query()
    job = MigrationJob(CalendarSource(calendar), IcsExportTarget("./calendar-export"))
    job.plan()
    job.run()
    print(job.verify().summary())

Import it into another calendar::

    from office365.migration.outlook import CalendarImportOptions, CalendarTarget, IcsTreeSource

    options = CalendarImportOptions()
    target = client.me.calendars.add(name="Imported").execute_query()
    job = MigrationJob(IcsTreeSource("./calendar-export", options), CalendarTarget(target, options))
    job.plan()
    job.run()
    print(job.verify().summary())

Pass the *same* options object to both sides of an import: the source computes the
content digest of what the target promises to restore.

Export layout (the same convention the mail export uses)::

    <root>/<calendar>/<YYYY-MM-DD>_<subject-slug>_<id-digest>.ics   iCalendar document
    <root>/<calendar>/<same stem>.json                              sidecar record
    <root>/manifest.jsonl                                           one sidecar per line

One calendar per source: Graph exposes each calendar as its own event collection,
so a mailbox with several calendars is a job per calendar (or a loop), which also
keeps each export directory self-describing.

Six honest limits, all measured against Exchange:

* A recurring event is exported **once**, as its series master (``RRULE`` in the
  ``.ics``, ``recurrence`` in the sidecar); the individual occurrences are not
  separate items, because importing them would duplicate the series.
* Cancelled events are tombstones, skipped by default
  (``CalendarExportOptions.include_cancelled``): replaying one as a live meeting
  would be worse than losing the record of the cancellation.
* An ``.ics`` is a courtesy for other clients. Everything is also in the sidecar,
  which is what an import reads — iCalendar cannot carry Graph's recurrence object,
  the online-meeting provider, or the sensitivity/importance pair without loss.
* Attendees are **not re-added by default**: creating an event with attendees makes
  Exchange mail an invitation to each of them, so a historical import would spam
  people with meetings they already had. ``CalendarImportOptions.restore_attendees``
  turns it on, and the run reports how many entries were left out.
* Exchange assigns the meeting metadata on create — ``iCalUid``, the organizer,
  attendee responses, ``created``/``modified`` — so those cannot be restored, and
  the imported event is organised by the importing mailbox.
* The body is re-serialized (an HTML body gains Exchange's ``<head>``/``<style>``
  wrapper), which is why an import is verified by an event digest rather than by
  bytes.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from office365.migration.adapters import DataSource, DataTarget, MigrationProgress
from office365.migration.base import MigrationItem
from office365.migration.outlook.adapters import SidecarTreeTarget
from office365.migration.outlook.calendar_models import (
    EVENT_COLUMNS,
    STANDALONE_EVENT_TYPES,
    CalendarExportOptions,
    CalendarImportOptions,
    event_create_payload,
    event_dedup_key,
    event_dest_path,
    event_digest,
    event_envelope,
    event_ics,
    event_key,
)
from office365.migration.outlook.eml_import import SIDECAR_SUFFIX
from office365.migration.outlook.models import mail_slug
from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.converters.scalars import iso_or_none
from office365.runtime.http.prefer import prefer_outlook_timezone
from office365.runtime.operations import emit_progress
from office365.runtime.queries.create_entity import CreateEntityQuery

#: Properties an import reads back off the target calendar to recognise its own work.
_EXISTING_COLUMNS = ["id", "subject", "start", "iCalUid"]

#: Graph's error code for a reused ``transactionId`` (a concurrent run got there first).
_DUPLICATE_TRANSACTION = "ErrorDuplicateTransactionId"


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


class IcsTreeSource(DataSource):
    """Reads an exported calendar tree back as migration items.

    The ``.ics`` is the payload (what another client would open); the JSON sidecar is
    the record the import replays, and it is **required** — an ``.ics`` alone cannot
    express Graph's recurrence object, and reading a calendar back out of iCalendar
    would invent an import that silently turns every series into a single meeting.
    """

    def __init__(self, root: str | Path, options: CalendarImportOptions | None = None) -> None:
        self._root = Path(root)
        self._options = options or CalendarImportOptions()
        self._items: dict[str, MigrationItem] = {}

    @property
    def root(self) -> Path:
        return self._root

    def label(self) -> str:
        return f"ics:{self._root}"

    def list_items(self, progress: MigrationProgress = None) -> list[MigrationItem]:
        if not self._root.is_dir():
            raise FileNotFoundError(f"{self._root} is not a directory of exported .ics files")
        items: list[MigrationItem] = []
        for path in sorted(self._root.rglob("*.ics")):
            item = self._item(path)
            self._items[item.dest_path] = item
            items.append(item)
            emit_progress(progress, done=len(items), stage="planning", items=[item])
        return items

    def _item(self, path: Path) -> MigrationItem:
        dest = path.relative_to(self._root).as_posix()
        envelope = self._sidecar(path)
        return MigrationItem(
            source_path=dest,
            dest_path=dest,
            size_bytes=path.stat().st_size,
            item_type="event",
            modified=envelope.get("modified"),
            created=envelope.get("created") or envelope.get("modified"),
            source_id=envelope.get("graph_id") or envelope.get("ical_uid"),
            metadata=envelope,
        )

    def _sidecar(self, path: Path) -> dict[str, Any]:
        sidecar = path.with_suffix(SIDECAR_SUFFIX)
        if not sidecar.exists():
            raise FileNotFoundError(
                f"{sidecar} is missing: the sidecar is the import contract (the .ics cannot carry the recurrence"
                " object Exchange needs), so the tree has to come from a calendar export"
            )
        return json.loads(sidecar.read_text(encoding="utf-8"))

    def _path(self, item: MigrationItem) -> Path:
        path = self._root / item.dest_path
        if self._root.resolve() not in path.resolve().parents:
            raise ValueError(f"{item.dest_path!r} escapes the export tree")
        return path

    def read(self, item: MigrationItem) -> bytes:
        """The event's ``.ics`` document."""
        return self._path(item).read_bytes()

    def checksum(self, item: MigrationItem) -> str:
        """The digest a calendar target can also compute, not the ``.ics`` bytes.

        The target is Exchange, which re-serializes the body and assigns the meeting
        metadata, so there is nothing on the other side to compare the bytes with;
        the event's restorable fields are what both sides can hold.
        """
        return event_digest(item.metadata or {}, self._options)


class CalendarTarget(DataTarget):
    """Recreates exported events in a Graph calendar.

    The source of truth is the sidecar, not the ``.ics``: Graph's request body is
    posted verbatim (:func:`event_create_payload`), because the typed helpers mangle
    the time zone and drop the ``transactionId``.
    """

    def __init__(self, calendar, options: CalendarImportOptions | None = None) -> None:
        self._calendar = calendar
        self._options = options or CalendarImportOptions()
        self._index: dict[tuple[str, str | None, str | None], list[Any]] | None = None
        self._claimed: dict[tuple[str, str | None, str | None], int] = {}
        self._present: dict[str, Any] = {}  # dest path -> created/found event
        self._attendees_dropped = 0
        #: Warnings a caller collects (the resolver convention).
        self.warnings: list[str] = []

    @property
    def calendar(self):
        return self._calendar

    def label(self) -> str:
        name = getattr(self._calendar, "name", None) or self._calendar.id
        return f"calendar:{name}"

    # -- target contract -------------------------------------------------------

    def exists(self, item: MigrationItem) -> bool:
        """Whether an equal event is already in the target calendar.

        Matched on subject plus start, because nothing the source knows survives the
        create (a created event comes back with ``iCalUid: null`` and a fresh id).
        Duplicates *at the source* are honoured: the index keeps a list per key and
        each source item claims its own entry, so two same-titled events at the same
        hour are still imported twice.
        """
        if item.dest_path in self._present:
            return True
        key = event_dedup_key(item.metadata or {})
        candidates = self._target_index().get(key) or []
        claimed = self._claimed.get(key, 0)
        if claimed >= len(candidates):
            return False
        self._claimed[key] = claimed + 1
        self._present[item.dest_path] = candidates[claimed]
        return True

    def write(self, item: MigrationItem, payload: Any) -> None:
        """Create the event from its sidecar record.

        ``payload`` (the ``.ics`` bytes) is deliberately unused: Graph's create body is
        the record's fields, and re-parsing the iCalendar would lose the recurrence
        object the export preserved precisely so this could be exact.
        """
        if item.item_type != "event":
            raise ValueError(f"a calendar imports events, not {item.item_type!r} ({item.dest_path})")
        envelope = item.metadata or {}
        try:
            body = event_create_payload(envelope, self._options)
        except ValueError as e:
            raise ValueError(f"{item.dest_path}: {e}") from None
        collection = self._calendar.events
        event = collection.create_typed_object()
        collection.context.add_query(CreateEntityQuery(collection, body, event))
        try:
            collection.context.execute_query()
        except ClientRequestException as e:
            adopted = self._adopt_duplicate(e, item)
            if adopted is None:
                raise
            self._present[item.dest_path] = adopted
            return
        self._attendees_dropped += _dropped_attendees(envelope, self._options)
        self._present[item.dest_path] = event
        key = event_dedup_key(envelope)
        self._target_index().setdefault(key, []).append(event)
        self._claimed[key] = self._claimed.get(key, 0) + 1

    def list_paths(self) -> Iterable[str]:
        """The destination paths this target has created or recognised.

        A calendar cannot be enumerated back into export paths (the paths carry the
        source's date slug), so extras are not reported: the validator's presence pass
        covers what the plan expects, and the target-side extras are events the user
        already had.
        """
        return sorted(self._present)

    def checksum(self, item: MigrationItem) -> str:
        """Fingerprint of the event as the target calendar returns it.

        The re-read asks for the *source item's* timezone (``Prefer:
        outlook.timezone``): Exchange renders event times in the signed-in mailbox's
        own zone otherwise, so a migration into a mailbox set to another zone would
        report every event as a content mismatch while the instants were identical
        (measured: ``09:00 W. Europe`` reads back as ``07:00 UTC`` unasked).
        """
        event = self._present.get(item.dest_path)
        if event is None:
            return ""
        read = self._calendar.events[event.id]
        read.select(EVENT_COLUMNS).get()
        zone = ((item.metadata or {}).get("start") or {}).get("timeZone")
        if zone:
            read.before_execute(_prefer_zone(zone))
        self._calendar.context.execute_query()
        return event_digest(event_envelope(read, ""), self._options)

    def commit(self, options: Any = None) -> None:  # noqa: ARG002 — runner hook signature
        """Report once what the run deliberately did not restore."""
        if self._attendees_dropped:
            self.warnings.append(
                f"{self._attendees_dropped} attendee entries were not restored: re-adding them makes Exchange"
                " send an invitation to every attendee of every imported event (measured), so it is opt-in —"
                " pass CalendarImportOptions(restore_attendees=True) to replay them"
            )

    # -- helpers ---------------------------------------------------------------

    def _target_index(self) -> dict[tuple[str, str | None, str | None], list[Any]]:
        """The target calendar's events, grouped by the key an import recognises."""
        if self._index is None:
            index: dict[tuple[str, str | None, str | None], list[Any]] = {}
            for event in self._calendar.events.select(_EXISTING_COLUMNS).get_all().execute_query():
                key = event_dedup_key({"subject": event.get_property("subject"), "start": event.get_property("start")})
                index.setdefault(key, []).append(event)
            self._index = index
        return self._index

    def _adopt_duplicate(self, error: Exception, item: MigrationItem) -> Any:
        """The event a concurrent run created with our ``transactionId``, if any.

        The id is derived from the source event, so a collision means the interesting
        work is already done — adopting the event keeps the run idempotent instead of
        failing on a resume that overlapped another.
        """
        if _DUPLICATE_TRANSACTION not in str(error):
            return None
        self._index = None
        candidates = self._target_index().get(event_dedup_key(item.metadata or {})) or []
        return candidates[-1] if candidates else None


def _prefer_zone(zone: str):
    """A ``before_execute`` hook that renders the read in ``zone``."""

    def handler(request) -> None:
        prefer_outlook_timezone(request, zone)

    return handler


def _dropped_attendees(envelope: dict[str, Any], options: CalendarImportOptions) -> int:
    """How many attendee entries the import left out."""
    if options.restore_attendees:
        return 0
    return sum(1 for item in envelope.get("attendees") or [] if isinstance(item, dict) and item.get("address"))


__all__ = ["CalendarSource", "CalendarTarget", "IcsExportTarget", "IcsTreeSource"]
