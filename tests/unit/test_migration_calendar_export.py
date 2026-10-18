"""Calendar export: a Graph calendar as a source, an ICS tree as the target (offline).

The transport scripts Graph the way the service answers: one page of events for the
calendar, and the calendar's own properties. The event shapes below are the ones the
Exchange-backed endpoint really returns (measured: ``start``/``end`` are wall-clock
literals with a zone name, recurrence is a pattern/range object).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from office365.graph_client import GraphClient
from office365.migration import MigrationJob
from office365.migration.outlook import (
    MANIFEST_NAME,
    CalendarExportOptions,
    CalendarSource,
    IcsExportTarget,
)
from office365.migration.outlook.calendar_models import MAX_LINE_OCTETS, event_ics
from tests._scripted_transport import MethodRoutingTransport

_CALENDAR = {"id": "cal-1", "name": "Calendar"}

_SINGLE = {
    "id": "e1",
    "iCalUid": "040000008200E00074C5B7101A82E0080000000",
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
    "iCalUid": None,
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
    "iCalUid": "040000008200E00074C5B7101A82E0080000000series",
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
    "iCalUid": "040000008200E00074C5B7101A82E0080000000series",
    "type": "occurrence",
    "seriesMasterId": "e3",
    "recurrence": None,
    "start": {"dateTime": "2026-03-16T09:00:00.0000000", "timeZone": "UTC"},
    "end": {"dateTime": "2026-03-16T09:15:00.0000000", "timeZone": "UTC"},
}

_CANCELLED = {
    **_SINGLE,
    "id": "e5",
    "iCalUid": "040000008200E00074C5B7101A82E0080000000cancelled",
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


def test_source_skips_occurrences_and_cancellations_by_default():
    transport = _transport()
    items = CalendarSource(_calendar(_client(transport))).list_items()

    assert not any("standup" in item.dest_path and "2026-03-16" in item.dest_path for item in items)  # occurrence
    assert not any("Cancelled" in item.dest_path for item in items)


def test_source_can_export_occurrences_and_cancellations():
    transport = _transport()
    options = CalendarExportOptions(include_recurring_instances=True, include_cancelled=True)

    items = CalendarSource(_calendar(_client(transport)), options).list_items()

    assert len(items) == 5  # noqa: PLR2004 — every scripted event, instances and tombstones included
    assert any("Cancelled-1-1" in item.dest_path for item in items)
    # Each instance has its own Graph id, and the date keeps the two names readable.
    assert sum(1 for item in items if "Weekly-standup" in item.dest_path) == 2  # noqa: PLR2004 — series + occurrence


def test_source_records_the_envelope_an_import_replays():
    transport = _transport()
    item = CalendarSource(_calendar(_client(transport))).list_items()[0]

    envelope = item.metadata
    assert item.source_id == "e1"  # the Graph id, not iCalUid: see event_key()
    assert envelope["ical_uid"] == _SINGLE["iCalUid"]
    assert envelope["subject"] == "Quarterly review; budget, headcount"
    assert envelope["start"] == {"dateTime": "2026-03-02T09:00:00.0000000", "timeZone": "Europe/Kiev"}
    assert envelope["body"] == {"content_type": "html", "content": "<p>Agenda: <b>Q1</b></p>"}
    assert envelope["attendees"][0] == {
        "name": "Bob",
        "address": "bob@contoso.com",
        "type": "required",
        "response": "accepted",
    }
    assert envelope["organizer"] == {"name": "Alice", "address": "alice@contoso.com"}
    assert envelope["categories"] == ["Finance", "Q1"]
    assert (envelope["show_as"], envelope["sensitivity"], envelope["importance"]) == ("tentative", "private", "high")
    assert envelope["join_url"] == "https://teams.microsoft.com/l/meetup-join/1"
    assert envelope["reminder_minutes"] == 15  # noqa: PLR2004
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
    assert f"UID:{_SINGLE['iCalUid']}\r\n" in text
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


def test_ics_writes_an_all_day_event_as_a_date_range():
    transport = _transport()
    items = CalendarSource(_calendar(_client(transport))).list_items()

    text = event_ics(items[1].metadata).decode("utf-8")

    assert "DTSTART;VALUE=DATE:20260305\r\n" in text
    assert "DTEND;VALUE=DATE:20260306\r\n" in text
    assert "TRANSP:TRANSPARENT\r\n" not in text.replace("STATUS:TENTATIVE", "")  # an OOF day is opaque
    assert "UID:e2" in text  # no iCalUid: the Graph id is the fallback identity


def test_ics_renders_a_recurrence_pattern_as_an_rrule():
    transport = _transport()
    items = CalendarSource(_calendar(_client(transport))).list_items()

    text = event_ics(items[2].metadata).decode("utf-8")

    assert "RRULE:FREQ=WEEKLY;BYDAY=MO,WE;COUNT=6\r\n" in text


def test_ics_folds_every_line_within_the_rfc_limit():
    transport = _transport()
    item = CalendarSource(_calendar(_client(transport))).list_items()[0]
    envelope = {**item.metadata, "subject": "Long " + "subject " * 30}

    raw = event_ics(envelope)

    for line in raw.split(b"\r\n"):
        assert len(line) <= MAX_LINE_OCTETS, line
    assert raw.count(b"\r\n ") >= 1  # at least one continuation line
    # Folding is reversible: unfolding restores the original summary.
    unfolded = raw.replace(b"\r\n ", b"").decode("utf-8")
    assert "SUMMARY:Long subject subject " in unfolded


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


def test_export_verifies_by_checksum(tmp_path: Path):
    client = _client(_transport())
    job = MigrationJob(CalendarSource(_calendar(client)), IcsExportTarget(tmp_path / "export"))

    job.plan()
    job.run()
    report = job.verify()

    assert (report.checked, report.mismatches) == (3, [])  # noqa: PLR2004


def test_export_is_reproducible(tmp_path: Path):
    def export(destination: Path) -> dict[str, bytes]:
        client = _client(_transport())
        job = MigrationJob(CalendarSource(_calendar(client)), IcsExportTarget(destination))
        job.plan()
        job.run()
        return {
            path.relative_to(destination).as_posix(): path.read_bytes() for path in sorted(destination.rglob("*.ics"))
        }

    first = export(tmp_path / "a")
    second = export(tmp_path / "b")

    assert first.keys() == second.keys()
    # Byte-identical: the document depends on the event, not on when it was exported.
    for path, payload in first.items():
        assert payload == second[path], path
