"""The calendar's spelling is data: pinned tables, a golden document, a stable digest.

Three things are asserted here, all of them about *where* an answer lives rather than
what one particular export happened to write:

* every :class:`IcsProfile` row names a member its generated enum declares — a token for a
  word the service never sends is a lie, and a renamed member is a row that silently
  stops matching;
* the tables that are meant to be complete cover their enum, so a value the service gains
  cannot quietly render as nothing;
* :data:`COMPARED` decides what a digest sees — a field's gate keeps it out of the
  verification when the import declines to restore it.

The golden document is the codec's whole contract in one assertion: line order, folding
at 75 octets, and which token each Graph word became.
"""

from __future__ import annotations

import hashlib
import json

import pytest
from office365.migration.outlook.calendar_codec import MAX_LINE_OCTETS, encode, rrule
from office365.migration.outlook.calendar_models import (
    CalendarImportOptions,
    event_canonical,
    event_digest,
)
from office365.migration.outlook.calendar_profile import COMPARED, ICALENDAR
from office365.outlook.calendar.attendees.type import AttendeeType
from office365.outlook.calendar.dayofweek import DayOfWeek
from office365.outlook.calendar.events.sensitivity import Sensitivity
from office365.outlook.calendar.meetingtimes.freebusystatus import FreeBusyStatus
from office365.outlook.mail.body_type import BodyType
from office365.outlook.mail.importance import Importance
from office365.outlook.mail.messages.responsetype import ResponseType
from office365.outlook.mail.recurrencepatterntype import RecurrencePatternType
from office365.outlook.mail.weekindex import WeekIndex

#: The dialect as a table: (the mapping, the generated enum it must agree with, whether
#: every member carries a token). ``transp``/``status`` are the two that spell only what a
#: reader cannot assume — a busy event carries no ``TRANSP``, an accepted one no ``STATUS``.
TABLES = [
    (ICALENDAR.transp, FreeBusyStatus, False),
    (ICALENDAR.status, FreeBusyStatus, False),
    (ICALENDAR.classification, Sensitivity, True),
    (ICALENDAR.priority, Importance, True),
    (ICALENDAR.role, AttendeeType, True),
    (ICALENDAR.partstat, ResponseType, True),
    (ICALENDAR.weekdays, DayOfWeek, True),
    (ICALENDAR.week_index, WeekIndex, True),
    (ICALENDAR.frequency, RecurrencePatternType, True),
    (ICALENDAR.body_field, BodyType, True),
]

#: A sidecar with one of everything, so the golden document exercises every branch the
#: writer has: an escaped subject, an HTML body, an attendee with and without a name,
#: categories, a classification, a reminder, and a join URL long enough to fold. The keys
#: are the model's own (``Event.to_json()``) plus the export's provenance.
SIDECAR = {
    "id": "e1",
    "iCalUId": "UID-1",
    "calendar_path": "Calendar",
    "calendar_display_path": "Calendar",
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
    "ics_path": "Calendar/2026-03-02_quarterly_review_12345678.ics",
}

#: The document :data:`SIDECAR` renders to, byte for byte. Folded lines are written out
#: with their continuation space, exactly as they land on disk.
GOLDEN = (
    "BEGIN:VCALENDAR\r\n"
    "VERSION:2.0\r\n"
    "PRODID:-//office365-rest-python-client//migration//EN\r\n"
    "CALSCALE:GREGORIAN\r\n"
    "METHOD:PUBLISH\r\n"
    "BEGIN:VEVENT\r\n"
    "UID:UID-1\r\n"
    "DTSTAMP:20260220T113000Z\r\n"
    "DTSTART;TZID=Europe/Kiev:20260302T090000\r\n"
    "DTEND;TZID=Europe/Kiev:20260302T100000\r\n"
    "SUMMARY:Quarterly review\\; budget\\, headcount\r\n"
    "LOCATION:Room 1\r\n"
    "X-ALT-DESC;FMTTYPE=text/html:<p>Agenda: <b>Q1</b></p>\r\n"
    "CATEGORIES:Finance,Q1\r\n"
    "CLASS:PRIVATE\r\n"
    "PRIORITY:1\r\n"
    "STATUS:TENTATIVE\r\n"
    'ORGANIZER;CN="Alice":mailto:alice@contoso.com\r\n'
    'ATTENDEE;CN="Bob";ROLE=REQ-PARTICIPANT;PARTSTAT=ACCEPTED;RSVP=TRUE:mailto:\r\n'
    " bob@contoso.com\r\n"
    "ATTENDEE;ROLE=OPT-PARTICIPANT;PARTSTAT=NEEDS-ACTION;RSVP=TRUE:mailto:carol\r\n"
    " @contoso.com\r\n"
    "X-MICROSOFT-SKYPETEAMSMEETINGURL:https://teams.microsoft.com/l/meetup-join\r\n"
    " /1\r\n"
    "BEGIN:VALARM\r\n"
    "ACTION:DISPLAY\r\n"
    "TRIGGER:-PT15M\r\n"
    "DESCRIPTION:Quarterly review\\; budget\\, headcount\r\n"
    "END:VALARM\r\n"
    "END:VEVENT\r\n"
    "END:VCALENDAR\r\n"
)


def test_the_codec_renders_the_golden_document():
    assert encode(SIDECAR).decode("utf-8") == GOLDEN


def test_every_table_row_names_a_member_the_model_declares():
    for table, enum, complete in TABLES:
        members = {member.name for member in enum}
        unknown = set(table) - members
        assert not unknown, f"{enum.__name__} does not declare {sorted(unknown)}: a row for a word nothing sends"
        if complete:
            assert set(table) == members, f"{enum.__name__} members with no {enum.__name__} → token row"


def test_the_partial_tables_spell_only_what_a_reader_cannot_assume():
    """The two incomplete tables are incomplete on purpose: their absence *is* the token."""
    assert set(ICALENDAR.transp) < {member.name for member in FreeBusyStatus}
    assert set(ICALENDAR.status) < {member.name for member in FreeBusyStatus}
    assert set(ICALENDAR.transp.values()) <= {"TRANSPARENT", "OPAQUE"}
    assert set(ICALENDAR.status.values()) <= {"TENTATIVE", "CONFIRMED", "CANCELLED"}


@pytest.mark.parametrize(
    ("pattern", "expected"),
    [
        ({"type": "daily", "interval": 3}, "FREQ=DAILY;INTERVAL=3"),
        ({"type": "weekly", "daysOfWeek": ["monday", "wednesday"]}, "FREQ=WEEKLY;BYDAY=MO,WE"),
        ({"type": "absoluteMonthly", "dayOfMonth": 15}, "FREQ=MONTHLY;BYMONTHDAY=15"),
        (
            {"type": "relativeMonthly", "daysOfWeek": ["tuesday"], "index": "last"},
            "FREQ=MONTHLY;BYDAY=-1TU",
        ),
        ({"type": "absoluteYearly", "month": 3, "dayOfMonth": 2}, "FREQ=YEARLY;BYMONTH=3;BYMONTHDAY=2"),
        (
            {"type": "relativeYearly", "month": 11, "daysOfWeek": ["thursday"], "index": "first"},
            "FREQ=YEARLY;BYMONTH=11;BYDAY=1TH",
        ),
    ],
)
def test_the_frequency_table_spells_every_pattern_the_service_sends(pattern, expected):
    assert rrule({"pattern": pattern, "range": {"type": "noEnd"}}) == expected


def test_a_folded_line_never_exceeds_the_octet_limit():
    document = encode({**SIDECAR, "subject": "\u00e9" * 200})
    for line in document.split(b"\r\n"):
        assert len(line) <= MAX_LINE_OCTETS


def test_the_digest_is_stable_across_the_split():
    """A sidecar's digest is computed by both sides of an import, so it must not drift."""
    assert event_digest(SIDECAR) == "4a8cc8de9a99d71953700f67e72cb593"


def test_a_gated_field_leaves_the_digest_when_the_import_declines_to_restore_it():
    options = CalendarImportOptions(restore_attendees=False)
    someone_else = [{"emailAddress": {"address": "someone@else.test"}, "type": "required"}]
    assert event_digest(SIDECAR, options) == event_digest({**SIDECAR, "attendees": someone_else}, options)
    restoring = CalendarImportOptions(restore_attendees=True)
    assert event_digest(SIDECAR, restoring) != event_digest({**SIDECAR, "attendees": someone_else}, restoring)


def test_the_comparison_profile_covers_the_sidecars_own_bookkeeping_only_by_omission():
    """Provenance is not content: the Graph id, the path and the calendar stay out."""
    compared = {rule.key for rule in COMPARED}
    assert compared.isdisjoint({"id", "iCalUId", "ics_path", "calendar_path", "calendar_display_path"})
    assert {"start", "end", "subject", "body", "attendees", "categories"} <= compared


def test_the_digest_is_the_md5_of_the_canonical_form():
    canonical = json.dumps(event_canonical(SIDECAR), sort_keys=True, default=str)
    assert event_digest(SIDECAR) == hashlib.md5(canonical.encode("utf-8")).hexdigest()
