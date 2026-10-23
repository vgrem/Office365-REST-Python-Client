"""Calendar import: an ICS sidecar tree as the source, a Graph calendar as the target.

The transport scripts Exchange the way it answers: a `POST /events` that echoes the
event it created (assigning ``iCalUid``, the organizer and the attendee responses), a
calendar listing used to recognise what an earlier run already created, and a read
that hands the event back **re-serialized** — Exchange wraps every HTML body in its
own ``<html><head><style>…`` envelope, which is why an import cannot be verified by
bytes.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from office365.graph_client import GraphClient
from office365.migration import MigrationJob
from office365.migration.base import MigrationItem
from office365.migration.outlook import (
    CalendarImportOptions,
    CalendarTarget,
    IcsTreeSource,
    event_create_payload,
    event_dedup_key,
    event_digest,
)
from office365.migration.outlook.calendar_models import event_transaction_id
from tests._scripted_transport import MethodRoutingTransport

_CALENDAR = {"id": "cal-2", "name": "Imported"}

#: The exchange-side wrapper Exchange puts around every body it accepts.
_WRAPPER = (
    '<html><head><meta name="Generator" content="Microsoft Exchange Server">'
    "<style><!-- .EmailQuote {{}} --></style></head><body>"
)

#: Hours ahead of UTC in March 2026, for the zones this fake speaks.
_ZONE_HOURS = {"UTC": 0, "W. Europe Standard Time": 2, "Europe/Kiev": 3}

#: The zone Exchange renders event times in when a read does not ask for another —
#: the signed-in mailbox's own (``09:00 Europe/Kiev`` reads back as ``06:00 UTC``,
#: measured live against Exchange).
_MAILBOX_ZONE = "UTC"


def _envelope(**overrides: Any) -> dict[str, Any]:
    envelope: dict[str, Any] = {
        "id": "e1",
        "iCalUId": None,
        "subject": "Quarterly review",
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
            {
                "emailAddress": {"address": "carol@contoso.com"},
                "type": "optional",
                "status": {"response": "none"},
            },
        ],
        "categories": ["Finance", "Q1"],
        "isReminderOn": True,
        "reminderMinutesBeforeStart": 15,
        "createdDateTime": "2026-02-01T08:00:00+00:00",
        "lastModifiedDateTime": "2026-02-20T11:30:00+00:00",
        "type": "singleInstance",
        "seriesMasterId": None,
        "recurrence": None,
        "isOnlineMeeting": False,
        "onlineMeetingProvider": None,
        "onlineMeeting": None,
        "hasAttachments": False,
        "webLink": "https://outlook.office365.com/owa/?itemid=e1",
        "ics_path": "Imported/2026-03-02_Quarterly-review_e1.ics",
    }
    envelope.update(overrides)
    return envelope


_SERIES = _envelope(
    id="e3",
    iCalUId="040000008200E00074C5B7101A82E0080000000series",
    subject="Weekly standup",
    start={"dateTime": "2026-03-09T09:00:00.0000000", "timeZone": "Europe/Kiev"},
    end={"dateTime": "2026-03-09T09:15:00.0000000", "timeZone": "Europe/Kiev"},
    attendees=[],
    categories=[],
    location=None,
    locations=[],
    webLink=None,
    recurrence={
        "pattern": {"type": "weekly", "interval": 1, "daysOfWeek": ["monday"], "firstDayOfWeek": "monday"},
        "range": {"type": "numbered", "startDate": "2026-03-09", "numberOfOccurrences": 6},
    },
)


def _preferred_zone(prefer: str) -> str | None:
    """The zone a ``Prefer: outlook.timezone="…"`` header asks a read to render in."""
    marker = 'outlook.timezone="'
    start = prefer.find(marker)
    if start == -1:
        return None
    rest = prefer[start + len(marker) :]
    return rest.split('"', 1)[0] or None


def _render(moment: dict[str, Any], zone: str) -> dict[str, Any]:
    """The same instant rendered in ``zone`` — what Exchange does on a read."""
    raw = str(moment.get("dateTime") or "")[:19]
    source = str(moment.get("timeZone") or _MAILBOX_ZONE)
    if not raw:
        return moment
    shifted = datetime.strptime(raw, "%Y-%m-%dT%H:%M:%S") + timedelta(
        hours=_ZONE_HOURS.get(zone, 0) - _ZONE_HOURS.get(source, 0)
    )
    return {"dateTime": shifted.strftime("%Y-%m-%dT%H:%M:%S") + ".0000000", "timeZone": zone}


class _Calendar:
    """A fake Exchange calendar: create, listing and read-back, with server-assigned bits."""

    def __init__(self, events: list[dict[str, Any]] | None = None, reject_duplicate: bool = False) -> None:
        self.events: dict[str, dict[str, Any]] = {event["id"]: event for event in events or []}
        self.posted: list[dict[str, Any]] = []
        #: The ``Prefer`` header of every read, in order.
        self.prefer: list[str] = []
        #: Answer the next create with Graph's duplicate-transaction error.
        self.reject_duplicate = reject_duplicate
        #: Events an earlier listing hid — a concurrent run creating one mid-import.
        self.hidden: set[str] = set()

    def routes(self):
        # Deeper routes first: ``/events/e1`` also contains ``/events``.
        return [
            ("GET", "/events/", self._read),
            ("POST", "/events", self._create),
            ("GET", "/events?", self._listing),
            (None, "/calendars/cal-2", _CALENDAR),
        ]

    def _listing(self, request):
        return {
            "value": [
                {"id": event["id"], "subject": event.get("subject"), "start": event.get("start"), "iCalUId": None}
                for event in self.events.values()
                if event["id"] not in self.hidden
            ]
        }

    def _read(self, request):
        event_id = request.url.split("/events/")[1].split("?")[0]
        prefer = request.headers.get("Prefer") or ""
        self.prefer.append(prefer)
        event = self.events[event_id]
        zone = _preferred_zone(prefer) or _MAILBOX_ZONE
        return {
            **event,
            "start": _render(event.get("start") or {}, zone),
            "end": _render(event.get("end") or {}, zone),
        }

    def _create(self, request):
        payload = request.data
        if isinstance(payload, str):
            payload = json.loads(payload)
        if self.reject_duplicate:
            self.reject_duplicate = False
            self.hidden.clear()  # the other run's event is visible to the re-read
            return {
                "http_status": 409,
                "body": {
                    "error": {
                        "code": "ErrorDuplicateTransactionId",
                        "message": "The transaction id was used to create a different event.",
                    }
                },
            }
        self.posted.append(payload)
        event = self._as_returned(payload, f"e{len(self.events) + 10}")
        self.events[event["id"]] = event
        return event

    @staticmethod
    def _as_returned(payload: dict[str, Any], event_id: str) -> dict[str, Any]:
        """What Exchange hands back for a created event: the payload, plus its own fields."""
        body = payload.get("body") or {}
        wrapped = _WRAPPER + str(body.get("content") or "") + "</body></html>" if body.get("content") else None
        return {
            "id": event_id,
            "iCalUId": None,  # measured: an event created through the API has no iCalUId
            "subject": payload.get("subject"),
            "body": {"contentType": "html", "content": wrapped},
            "start": payload.get("start"),
            "end": payload.get("end"),
            "isAllDay": bool(payload.get("isAllDay")),
            "isCancelled": False,
            "showAs": payload.get("showAs", "busy"),
            "sensitivity": payload.get("sensitivity", "normal"),
            "importance": payload.get("importance", "normal"),
            "location": payload.get("location") or {"displayName": None},
            "locations": payload.get("locations") or [],
            "organizer": {"emailAddress": {"name": "Marta Doe", "address": "mdoe@mediadev8.onmicrosoft.com"}},
            "attendees": [
                {**attendee, "status": {"response": "none", "time": "0001-01-01T00:00:00Z"}}
                for attendee in payload.get("attendees") or []
            ],
            "categories": payload.get("categories") or [],
            "isReminderOn": bool(payload.get("isReminderOn")),
            "reminderMinutesBeforeStart": payload.get("reminderMinutesBeforeStart", 0),
            "createdDateTime": "2026-03-02T12:00:00Z",  # server-assigned
            "lastModifiedDateTime": "2026-03-02T12:00:00Z",
            "type": "seriesMaster" if payload.get("recurrence") else "singleInstance",
            "seriesMasterId": None,
            "recurrence": payload.get("recurrence"),
            "isOnlineMeeting": False,
            "onlineMeetingProvider": "unknown",
            "onlineMeeting": None,
            "hasAttachments": False,
            "webLink": f"https://outlook.office365.com/owa/?itemid={event_id}",
        }


def _client(calendar: _Calendar) -> GraphClient:
    client = GraphClient()
    client.pending_request().beforeExecute.clear()
    client.pending_request().transport = MethodRoutingTransport(calendar.routes())
    return client


def _target(client: GraphClient, options: CalendarImportOptions | None = None) -> CalendarTarget:
    return CalendarTarget(client.me.calendars["cal-2"].get().execute_query(), options)


def _tree(root: Path, envelopes: dict[str, dict[str, Any]]) -> Path:
    """Write an exported calendar tree: an ``.ics`` plus the sidecar the export records."""
    for relative, envelope in envelopes.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"BEGIN:VCALENDAR\r\nEND:VCALENDAR\r\n")
        path.with_suffix(".json").write_text(json.dumps(envelope), encoding="utf-8")
    return root


def _root(tmp_path: Path, envelopes: dict[str, dict[str, Any]] | None = None) -> Path:
    return _tree(tmp_path / "export", envelopes or {"Imported/e1.ics": _envelope()})


# -- the source ----------------------------------------------------------------


def test_source_reads_the_sidecar_tree(tmp_path: Path):
    items = IcsTreeSource(_root(tmp_path, {"Imported/e1.ics": _envelope(), "Imported/e3.ics": _SERIES})).list_items()

    assert [item.dest_path for item in items] == ["Imported/e1.ics", "Imported/e3.ics"]
    assert all(item.item_type == "event" for item in items)
    assert items[0].metadata["subject"] == "Quarterly review"
    assert items[1].metadata["recurrence"]["pattern"]["type"] == "weekly"
    assert items[0].source_id == "e1"


def test_source_checksum_is_the_digest_the_target_can_compute(tmp_path: Path):
    item = IcsTreeSource(_root(tmp_path)).list_items()[0]

    assert IcsTreeSource(_root(tmp_path)).checksum(item) == event_digest(_envelope())


def test_source_refuses_an_ics_without_a_sidecar(tmp_path: Path):
    root = _root(tmp_path)
    (root / "Imported" / "e1.json").unlink()

    with pytest.raises(FileNotFoundError, match="the sidecar is the import contract"):
        IcsTreeSource(root).list_items()


def test_source_refuses_a_sidecar_that_escapes_the_tree(tmp_path: Path):
    source = IcsTreeSource(_root(tmp_path))
    item = MigrationItem("../../etc/passwd", "../../etc/passwd", 0, "event")

    with pytest.raises(ValueError, match="escapes the export tree"):
        source.read(item)


def test_source_refuses_a_directory_that_is_not_an_export(tmp_path: Path):
    with pytest.raises(FileNotFoundError, match="is not a directory of exported .ics files"):
        IcsTreeSource(tmp_path / "nope").list_items()


# -- the payload ---------------------------------------------------------------


def test_payload_keeps_the_wall_clock_zone_and_the_recurrence():
    payload = event_create_payload(_SERIES, context=GraphClient())

    assert payload["start"] == {"dateTime": "2026-03-09T09:00:00.0000000", "timeZone": "Europe/Kiev"}
    assert payload["recurrence"] == _SERIES["recurrence"]
    assert payload["transactionId"] == event_transaction_id(_SERIES)
    # Server-assigned: sending them back is at best ignored (measured on iCalUId).
    for owned in ("iCalUId", "organizer", "attendees", "createdDateTime"):
        assert owned not in payload, owned


def test_payload_carries_the_event_attributes_an_import_restores():
    payload = event_create_payload(_envelope(), context=GraphClient())

    assert payload["showAs"] == "tentative"
    assert payload["sensitivity"] == "private"
    assert payload["importance"] == "high"
    assert payload["location"] == {"displayName": "Room 1"}
    assert payload["locations"] == [{"displayName": "Room 1"}]
    assert payload["categories"] == ["Finance", "Q1"]
    assert (payload["isReminderOn"], payload["reminderMinutesBeforeStart"]) == (True, 15)
    assert payload["body"] == {"contentType": "HTML", "content": "<p>Agenda: <b>Q1</b></p>"}


def test_payload_drops_attendees_unless_asked_because_they_would_be_invited():
    assert "attendees" not in event_create_payload(_envelope(), context=GraphClient())

    payload = event_create_payload(_envelope(), CalendarImportOptions(restore_attendees=True), context=GraphClient())
    assert payload["attendees"] == [
        {"emailAddress": {"address": "bob@contoso.com", "name": "Bob"}, "type": "required"},
        {"emailAddress": {"address": "carol@contoso.com"}, "type": "optional"},
    ]


def test_payload_refuses_a_recurrence_an_older_export_wrote_as_text():
    """The sidecar is the contract: a series it cannot express must not become a single meeting."""
    broken = _envelope(recurrence="PatternedRecurrence(pattern=RecurrencePattern(interval=1), range=…)")

    with pytest.raises(ValueError, match="re-export the calendar"):
        event_create_payload(broken, context=GraphClient())


def test_payload_requires_a_time_range():
    with pytest.raises(ValueError, match="no start/end dateTime"):
        event_create_payload(_envelope(start=None), context=GraphClient())


def test_transaction_id_is_deterministic_per_source_event():
    assert event_transaction_id(_envelope()) == event_transaction_id(_envelope())
    assert event_transaction_id(_envelope()) != event_transaction_id(_SERIES)


# -- the target ----------------------------------------------------------------


def test_import_creates_the_event_from_the_sidecar(tmp_path: Path):
    calendar = _Calendar()
    job = MigrationJob(IcsTreeSource(_root(tmp_path)), _target(_client(calendar)))

    job.plan()
    stats = job.run()

    assert stats.success == 1
    assert calendar.posted[0]["subject"] == "Quarterly review"
    assert calendar.posted[0]["start"]["timeZone"] == "Europe/Kiev"


def test_import_replays_a_series_as_a_series(tmp_path: Path):
    calendar = _Calendar()
    job = MigrationJob(IcsTreeSource(_root(tmp_path, {"Imported/e3.ics": _SERIES})), _target(_client(calendar)))

    job.plan()
    job.run()

    assert calendar.posted[0]["recurrence"]["pattern"]["daysOfWeek"] == ["monday"]
    assert calendar.events["e10"]["type"] == "seriesMaster"  # noqa: PLR2004 — the id the fake assigned


def test_import_verifies_the_event_across_the_server_rewrite(tmp_path: Path):
    """The read-back is asked for the source's zone, so the digest compares like with like."""
    calendar = _Calendar()
    job = MigrationJob(IcsTreeSource(_root(tmp_path)), _target(_client(calendar)))

    job.plan()
    job.run()
    report = job.verify()

    assert (report.checked, report.mismatches) == (1, [])
    assert calendar.prefer == ['outlook.timezone="Europe/Kiev"']


def test_import_reports_a_body_that_did_not_arrive(tmp_path: Path):
    calendar = _Calendar()
    job = MigrationJob(IcsTreeSource(_root(tmp_path)), _target(_client(calendar)))
    job.plan()
    job.run()
    calendar.events["e10"]["body"]["content"] = "<p>something else</p>"  # noqa: PLR2004 — the id the fake assigned

    report = job.verify()

    assert report.mismatches == ["content mismatch: Imported/e1.ics"]


def test_resume_skips_the_events_it_already_created(tmp_path: Path):
    calendar = _Calendar()
    root = _root(tmp_path)
    first = MigrationJob(IcsTreeSource(root), _target(_client(calendar)))
    first.plan()
    first.run()

    job = MigrationJob(IcsTreeSource(root), _target(_client(calendar)))
    job.plan()
    stats = job.run()

    assert (stats.success, stats.skipped) == (0, 1)
    assert len(calendar.posted) == 1  # noqa: PLR2004 — the first run's create, not a second copy


def test_two_source_events_with_the_same_subject_and_start_are_both_imported(tmp_path: Path):
    """A calendar can hold duplicates; recognising "already there" must not collapse them."""
    calendar = _Calendar()
    twin = _envelope(id="e2")
    root = _root(tmp_path, {"Imported/e1.ics": _envelope(), "Imported/e2.ics": twin})
    client = _client(calendar)

    job = MigrationJob(IcsTreeSource(root), _target(client))
    job.plan()
    assert job.run().success == 2  # noqa: PLR2004 — both twins, in one run

    again = MigrationJob(IcsTreeSource(root), _target(client))
    again.plan()
    assert again.run().skipped == 2  # noqa: PLR2004 — and both are recognised on the re-run


def test_a_duplicate_transaction_id_is_adopted_not_failed(tmp_path: Path):
    """A concurrent run that won the race means the work is done — adopt its event."""
    calendar = _Calendar(
        events=[
            {
                "id": "x1",
                **_Calendar._as_returned(
                    {"subject": "Quarterly review", "start": _envelope()["start"], "end": _envelope()["end"]}, "x1"
                ),
            }
        ]
    )
    calendar.reject_duplicate = True
    calendar.hidden = {"x1"}  # the listing ran before the other run created its event
    target = _target(_client(calendar))
    source = IcsTreeSource(_root(tmp_path))
    job = MigrationJob(source, target)

    job.plan()
    stats = job.run()

    assert stats.errors == 0
    assert stats.success == 1
    assert calendar.posted == []  # the fake refused the create; the event was adopted
    assert target.list_paths() == ["Imported/e1.ics"]
    assert target.checksum(source.list_items()[0]) != ""


def test_write_refuses_an_item_that_is_not_an_event(tmp_path: Path):
    target = _target(_client(_Calendar()))
    item = MigrationItem("x.txt", "x.txt", 10, "file")

    with pytest.raises(ValueError, match="imports events, not 'file'"):
        target.write(item, b"bytes")


def test_write_refuses_a_sidecar_without_a_time_range(tmp_path: Path):
    target = _target(_client(_Calendar()))
    item = MigrationItem("Imported/e1.ics", "Imported/e1.ics", 0, "event", metadata=_envelope(start=None))

    with pytest.raises(ValueError, match="Imported/e1.ics: the sidecar has no start/end"):
        target.write(item, b"")


def test_commit_reports_the_attendees_it_left_out(tmp_path: Path):
    calendar = _Calendar()
    target = _target(_client(calendar))
    job = MigrationJob(IcsTreeSource(_root(tmp_path)), target)

    job.plan()
    job.run()

    assert len(target.warnings) == 1
    assert "2 attendee entries were not restored" in target.warnings[0]
    assert "restore_attendees=True" in target.warnings[0]


def test_commit_stays_quiet_when_attendees_are_restored(tmp_path: Path):
    calendar = _Calendar()
    options = CalendarImportOptions(restore_attendees=True)
    target = _target(_client(calendar), options)
    job = MigrationJob(IcsTreeSource(_root(tmp_path), options), target)

    job.plan()
    job.run()

    assert target.warnings == []
    assert len(calendar.posted[0]["attendees"]) == 2  # noqa: PLR2004 — both, as asked


# -- the digest ----------------------------------------------------------------


def test_digest_ignores_what_the_service_owns():
    """Organizer, iCalUid, responses and timestamps are assigned, not restored."""
    restored = _envelope(
        organizer={"emailAddress": {"name": "Marta Doe", "address": "mdoe@microsoft.com"}}, iCalUId="ABC"
    )

    assert event_digest(restored, CalendarImportOptions()) == event_digest(_envelope(), CalendarImportOptions())


def test_digest_ignores_the_markup_exchange_adds():
    wrapped = _envelope(body={"contentType": "html", "content": _WRAPPER + "<p>Agenda: <b>Q1</b></p></body></html>"})

    assert event_digest(wrapped, CalendarImportOptions()) == event_digest(_envelope(), CalendarImportOptions())


def test_digest_notices_a_real_change():
    changed = _envelope(subject="Quarterly review (moved)")

    assert event_digest(changed, CalendarImportOptions()) != event_digest(_envelope(), CalendarImportOptions())


def test_digest_follows_the_options_for_attendees_and_categories():
    without = _envelope(attendees=[], categories=[])
    silent = CalendarImportOptions(restore_categories=False)
    strict = CalendarImportOptions(restore_attendees=True, restore_categories=True)

    # Each option decides whether its field is compared — attendees off, categories on by
    # default — so both sides of a job must agree on the options object.
    assert event_digest(without, silent) == event_digest(_envelope(), silent)
    assert event_digest(without, CalendarImportOptions()) != event_digest(_envelope(), CalendarImportOptions())
    assert event_digest(without, strict) != event_digest(_envelope(), strict)


def test_dedup_key_is_subject_and_start():
    assert event_dedup_key(_envelope()) == ("Quarterly review", "2026-03-02T09:00:00", "Europe/Kiev")
    assert event_dedup_key(_envelope(start=None)) == ("Quarterly review", None, None)
