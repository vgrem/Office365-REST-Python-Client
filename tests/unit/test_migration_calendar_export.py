"""Calendar export: a Graph calendar as a source, an ICS tree as the target (offline).

The transport scripts Graph the way the service answers: one page of events for the
calendar, and the calendar's own properties. The event shapes below are the ones the
Exchange-backed endpoint really returns (measured: ``start``/``end`` are wall-clock
literals with a zone name, recurrence is a pattern/range object).

The identity property is spelled ``iCalUId`` — capital ``ID`` — on the wire (measured:
``/me/calendar/events`` answers ``"iCalUId": "040000008200E00074C5B7101A82E008..."``),
which is also how the generated ``Event.ical_uid`` getter reads it. The fixtures used to
say ``iCalUid``, i.e. they agreed with the exporter's own typo instead of the service,
and so could not see that the field was being dropped.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from office365.graph_client import GraphClient
from office365.migration import MigrationJob
from office365.migration.outlook import (
    MANIFEST_NAME,
    CalendarSource,
    IcsExportTarget,
)
from office365.migration.outlook.calendar_models import EVENT_COLUMNS, event_ics
from office365.outlook.calendar.events.event import Event
from tests._scripted_transport import MethodRoutingTransport

_CALENDAR = {"id": "cal-1", "name": "Calendar"}

_SINGLE = {
    "id": "e1",
    "iCalUId": "040000008200E00074C5B7101A82E0080000000",
    "subject": "Quarterly review; budget, headcount",
    "body": {"contentType": "html", "content": "<p>Agenda: <b>Q1</b></p>"},
    "start": {"dateTime": "2026-03-02T09:00:00.0000000", "timeZone": "Europe/Kiev"},
    "end": {"dateTime": "2026-03-02T10:00:00.0000000", "timeZone": "Europe/Kiev"},
    "isAllDay": False,
    "isCancelled": False,
    "showAs": "tentative",
    "sensitivity": "private",
    "importance": "high",
    "location": {"displayName": "Room 1"},
    "locations": [{"displayName": "Room 1"}],
    "organizer": {"emailAddress": {"name": "Alice", "address": "alice@contoso.com"}},
    "attendees": [
        {
            "emailAddress": {"name": "Bob", "address": "bob@contoso.com"},
            "type": "required",
            "status": {"response": "accepted"},
        },
        {"emailAddress": {"address": "carol@contoso.com"}, "type": "optional", "status": {"response": "none"}},
    ],
    "categories": ["Finance", "Q1"],
    "isReminderOn": True,
    "reminderMinutesBeforeStart": 15,
    "createdDateTime": "2026-02-01T08:00:00Z",
    "lastModifiedDateTime": "2026-02-20T11:30:00Z",
    "type": "singleInstance",
    "seriesMasterId": None,
    "recurrence": None,
    "isOnlineMeeting": True,
    "onlineMeetingProvider": "teamsForBusiness",
    "onlineMeeting": {"joinUrl": "https://teams.microsoft.com/l/meetup-join/1"},
    "hasAttachments": False,
    "webLink": "https://outlook.office365.com/owa/?itemid=e1",
}

_ALL_DAY = {
    "id": "e2",
    "iCalUId": None,
    "subject": "Company offsite",
    "body": {"contentType": "text", "content": "All day"},
    "start": {"dateTime": "2026-03-05T00:00:00.0000000", "timeZone": "UTC"},
    "end": {"dateTime": "2026-03-06T00:00:00.0000000", "timeZone": "UTC"},
    "isAllDay": True,
    "isCancelled": False,
    "showAs": "oof",
    "sensitivity": "normal",
    "importance": "normal",
    "location": {"displayName": "Kyiv"},
    "locations": [{"displayName": "Kyiv"}],
    "organizer": {"emailAddress": {"name": "Alice", "address": "alice@contoso.com"}},
    "attendees": [],
    "categories": [],
    "isReminderOn": False,
    "reminderMinutesBeforeStart": 0,
    "createdDateTime": "2026-01-05T08:00:00Z",
    "lastModifiedDateTime": "2026-01-05T08:00:00Z",
    "type": "singleInstance",
    "recurrence": None,
    "isOnlineMeeting": False,
    "onlineMeeting": None,
    "hasAttachments": False,
}

_SERIES = {
    "id": "e3",
    "iCalUId": "040000008200E00074C5B7101A82E0080000000series",
    "subject": "Weekly standup",
    "body": {"contentType": "text", "content": "Standup"},
    "start": {"dateTime": "2026-03-09T09:00:00.0000000", "timeZone": "UTC"},
    "end": {"dateTime": "2026-03-09T09:15:00.0000000", "timeZone": "UTC"},
    "isAllDay": False,
    "isCancelled": False,
    "showAs": "busy",
    "sensitivity": "normal",
    "importance": "normal",
    "location": {"displayName": "Meet"},
    "locations": [],
    "organizer": {"emailAddress": {"address": "alice@contoso.com"}},
    "attendees": [],
    "categories": [],
    "isReminderOn": False,
    "reminderMinutesBeforeStart": 0,
    "createdDateTime": "2026-02-09T08:00:00Z",
    "lastModifiedDateTime": "2026-02-09T08:00:00Z",
    "type": "seriesMaster",
    "recurrence": {
        "pattern": {"type": "weekly", "interval": 1, "daysOfWeek": ["monday", "wednesday"]},
        "range": {"type": "numbered", "numberOfOccurrences": 6, "startDate": "2026-03-09"},
    },
    "isOnlineMeeting": False,
    "onlineMeeting": None,
    "hasAttachments": False,
}

_OCCURRENCE = {
    **_SERIES,
    "id": "e4",
    "iCalUId": "040000008200E00074C5B7101A82E0080000000series",
    "type": "occurrence",
    "seriesMasterId": "e3",
    "recurrence": None,
    "start": {"dateTime": "2026-03-16T09:00:00.0000000", "timeZone": "UTC"},
    "end": {"dateTime": "2026-03-16T09:15:00.0000000", "timeZone": "UTC"},
}

_CANCELLED = {
    **_SINGLE,
    "id": "e5",
    "iCalUId": "040000008200E00074C5B7101A82E0080000000cancelled",
    "subject": "Cancelled 1:1",
    "isCancelled": True,
    "start": {"dateTime": "2026-03-04T09:00:00.0000000", "timeZone": "UTC"},
    "end": {"dateTime": "2026-03-04T09:30:00.0000000", "timeZone": "UTC"},
}

_EVENTS = [_SINGLE, _ALL_DAY, _SERIES, _OCCURRENCE, _CANCELLED]


def _transport(events=None) -> MethodRoutingTransport:
    return MethodRoutingTransport(
        [
            # Deeper routes first: ``/me/calendar/events`` also contains ``/me/calendar``.
            (None, "/me/calendar/events", {"value": _EVENTS if events is None else events}),
            (None, "/me/calendar", _CALENDAR),
        ]
    )


def _client(transport: MethodRoutingTransport) -> GraphClient:
    client = GraphClient()
    client.pending_request().beforeExecute.clear()
    client.pending_request().transport = transport
    return client


def _calendar(client: GraphClient):
    return client.me.calendar.get().execute_query()


def _digest(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:8]


def test_source_enumerates_one_item_per_standalone_event():
    transport = _transport()
    items = CalendarSource(_calendar(_client(transport))).list_items()

    assert [item.dest_path for item in items] == [
        f"Calendar/2026-03-02_Quarterly-review-budget-headcount_{_digest('e1')}.ics",
        f"Calendar/2026-03-05_Company-offsite_{_digest('e2')}.ics",
        f"Calendar/2026-03-09_Weekly-standup_{_digest('e3')}.ics",
    ]
    assert all(item.item_type == "event" for item in items)


def test_source_records_the_envelope_an_import_replays():
    transport = _transport()
    item = CalendarSource(_calendar(_client(transport))).list_items()[0]

    envelope = item.metadata
    assert item.source_id == "e1"  # the Graph id, not iCalUid: see event_key()
    assert envelope["iCalUId"] == _SINGLE["iCalUId"]
    assert envelope["subject"] == "Quarterly review; budget, headcount"
    assert envelope["start"] == {"dateTime": "2026-03-02T09:00:00.0000000", "timeZone": "Europe/Kiev"}
    assert envelope["body"] == {"contentType": "html", "content": "<p>Agenda: <b>Q1</b></p>"}
    assert envelope["attendees"][0] == {
        "emailAddress": {"name": "Bob", "address": "bob@contoso.com"},
        "type": "required",
        "status": {"response": "accepted"},
    }
    assert envelope["organizer"] == {"emailAddress": {"name": "Alice", "address": "alice@contoso.com"}}
    assert envelope["categories"] == ["Finance", "Q1"]
    assert (envelope["showAs"], envelope["sensitivity"], envelope["importance"]) == ("tentative", "private", "high")
    assert envelope["onlineMeeting"] == {"joinUrl": "https://teams.microsoft.com/l/meetup-join/1"}
    assert envelope["reminderMinutesBeforeStart"] == 15  # noqa: PLR2004
    assert envelope["ics_path"] == item.dest_path
    assert envelope["calendar_display_path"] == "Calendar"
    assert item.created == "2026-02-01T08:00:00+00:00"
    assert item.modified == "2026-02-20T11:30:00+00:00"


def test_source_reads_the_ics_it_renders_and_counts_its_bytes():
    transport = _transport()
    source = CalendarSource(_calendar(_client(transport)))
    item = source.list_items()[0]

    assert item.size_bytes == 0  # an event has no size until the document exists
    data = source.read(item)
    assert data.startswith(b"BEGIN:VCALENDAR\r\n")
    assert item.size_bytes == len(data)
    # A file checksum, not a security use: the bytes are ours and reproducible.
    assert source.checksum(item) == hashlib.md5(data).hexdigest()


def test_ics_renders_time_ranges_attendees_and_reminders():
    transport = _transport()
    item = CalendarSource(_calendar(_client(transport))).list_items()[0]

    text = event_ics(item.metadata).decode("utf-8")
    unfolded = text.replace("\r\n ", "")  # a long content line is folded per RFC 5545

    assert "BEGIN:VEVENT\r\n" in text
    # The key is the Graph id (stable), the ICS UID is the iCalUid (what other
    # calendar clients match on) — the two identities are deliberately different.
    assert f"UID:{_SINGLE['iCalUId']}\r\n" in text
    assert "DTSTART;TZID=Europe/Kiev:20260302T090000\r\n" in text
    assert "DTEND;TZID=Europe/Kiev:20260302T100000\r\n" in text
    # The zone rides in TZID, so the wall clock is written unchanged (no UTC shift).
    assert "SUMMARY:Quarterly review\\; budget\\, headcount\r\n" in text
    assert "LOCATION:Room 1\r\n" in text
    assert "CATEGORIES:Finance,Q1\r\n" in text
    assert "CLASS:PRIVATE\r\n" in text
    assert "PRIORITY:1\r\n" in text
    assert "STATUS:TENTATIVE\r\n" in text
    assert 'ORGANIZER;CN="Alice":mailto:alice@contoso.com\r\n' in text
    assert 'ATTENDEE;CN="Bob";ROLE=REQ-PARTICIPANT;PARTSTAT=ACCEPTED;RSVP=TRUE:mailto:bob@contoso.com' in unfolded
    assert "ATTENDEE;ROLE=OPT-PARTICIPANT;PARTSTAT=NEEDS-ACTION;RSVP=TRUE:mailto:carol@contoso.com" in unfolded
    # iCalendar DESCRIPTION is TEXT: HTML rides in the standard X-ALT-DESC instead of
    # being flattened into a lossy plain-text approximation.
    assert "X-ALT-DESC;FMTTYPE=text/html:<p>Agenda: <b>Q1</b></p>" in text
    assert "DESCRIPTION:Agenda" not in text
    assert "TRIGGER:-PT15M" in text
    assert "X-MICROSOFT-SKYPETEAMSMEETINGURL:https://teams.microsoft.com/l/meetup-join/1" in unfolded
    assert "DTSTAMP:20260220T113000Z" in text  # the event's own mtime, never the export's
    assert text.endswith("END:VCALENDAR\r\n")


def test_export_writes_a_tree_a_sidecar_and_a_manifest(tmp_path: Path):
    export = tmp_path / "export"
    job = MigrationJob(CalendarSource(_calendar(_client(_transport()))), IcsExportTarget(export))

    job.plan()
    stats = job.run()

    planned = [item.dest_path for item in job.plan().items]
    assert stats.success == 3  # noqa: PLR2004
    assert stats.bytes_transferred > 0
    assert sorted(IcsExportTarget(export).list_paths()) == sorted(planned)
    sidecar = json.loads((export / planned[0]).with_suffix(".json").read_text(encoding="utf-8"))
    # The sidecar records the payload's path and size the way the mail export does, so
    # one index format covers both products.
    assert (sidecar["ics_path"], sidecar["size_bytes"] > 0) == (planned[0], True)
    manifest = (export / MANIFEST_NAME).read_text(encoding="utf-8").splitlines()
    assert len(manifest) == 3  # noqa: PLR2004
    assert json.loads(manifest[0])["ics_path"].endswith(".ics")


def test_export_writes_a_json_safe_sidecar(tmp_path: Path):
    """The sidecar is the import contract: a typed Graph value must not land as its ``repr``.

    ``recurrence`` arrives as a typed ``PatternedRecurrence``; dumping it with
    ``json.dumps(..., default=str)`` wrote ``PatternedRecurrence(pattern=…, range=…)``
    into every series' sidecar, which no import can read back.
    """
    transport = _transport()
    job = MigrationJob(CalendarSource(_calendar(_client(transport))), IcsExportTarget(tmp_path))
    job.plan()
    job.run()

    sidecars = sorted(tmp_path.rglob("*.json"))
    series = next(path for path in sidecars if "standup" in path.read_text(encoding="utf-8"))
    record = json.loads(series.read_text(encoding="utf-8"))

    assert isinstance(record["recurrence"], dict)
    assert record["recurrence"]["pattern"]["type"] == "weekly"
    assert record["recurrence"]["range"]["numberOfOccurrences"] == 6  # noqa: PLR2004 — from the scripted series
    # Enums travel as their wire name, not as ``FreeBusyStatus.tentative``.
    single = next(path for path in sidecars if "Quarterly-review" in path.read_text(encoding="utf-8"))
    single_record = json.loads(single.read_text(encoding="utf-8"))
    assert single_record["showAs"] == "tentative"
    assert isinstance(single_record["onlineMeetingProvider"], str)  # a wire name, not an enum repr


def test_export_verifies_by_checksum(tmp_path: Path):
    client = _client(_transport())
    job = MigrationJob(CalendarSource(_calendar(client)), IcsExportTarget(tmp_path / "export"))

    job.plan()
    job.run()
    report = job.verify()

    assert (report.checked, report.mismatches) == (3, [])  # noqa: PLR2004


def test_the_export_projection_is_the_model_projection():
    """``EVENT_COLUMNS`` is derived from the model, not kept beside it.

    It used to be a hand-kept list and had drifted: it named 33 columns and omitted
    ``isCancelled``, which the export filters on. A real ``$select`` answers only the
    columns it is given, so a cancelled event came back with ``is_cancelled: None``
    and was exported even though ``include_cancelled`` defaults to False. Deriving the
    projection makes that class of omission unrepresentable, and the navigation
    properties stay out of it automatically — ``$select`` rejects them.
    """
    assert EVENT_COLUMNS == Event.select_all()
    assert "isCancelled" in EVENT_COLUMNS
    assert not set(EVENT_COLUMNS) & set(Event.expandable())
