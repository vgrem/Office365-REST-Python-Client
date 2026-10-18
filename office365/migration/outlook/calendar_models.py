"""Calendar export model — the projection, the per-event record, and the ICS writer.

An exported event is two files: an ``.ics`` (the portable artefact — Outlook,
Google Calendar and Thunderbird all open it) and a JSON sidecar carrying what
iCalendar cannot express faithfully (Graph ids, the recurrence object Graph
normalises, the online-meeting provider, sensitivity/importance). The sidecar is
the import contract; the ``.ics`` is regenerated from it, so an export is
reproducible: the same event always produces the same bytes.

Unlike mail, this file is *built* rather than fetched, so a byte checksum is a
valid verification: there is no server re-serialization in the middle.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from office365.migration.outlook.models import mail_slug
from office365.runtime.converters.scalars import iso_or_none

#: Graph event properties an export reads. All of them are selectable in one
#: ``$select`` (each was probed against the Exchange-backed endpoint).
EVENT_COLUMNS = [
    "id",
    "iCalUid",
    "subject",
    "body",
    "bodyPreview",
    "start",
    "end",
    "isAllDay",
    "location",
    "locations",
    "organizer",
    "attendees",
    "categories",
    "showAs",
    "sensitivity",
    "importance",
    "isReminderOn",
    "reminderMinutesBeforeStart",
    "createdDateTime",
    "lastModifiedDateTime",
    "type",
    "seriesMasterId",
    "recurrence",
    "isOnlineMeeting",
    "onlineMeetingProvider",
    "onlineMeeting",
    "hasAttachments",
    "webLink",
    "transactionId",
    "responseStatus",
    "isOrganizer",
    "allowNewTimeProposals",
    "responseRequested",
]

#: Event types that stand on their own. An ``occurrence``/``exception`` belongs to
#: its ``seriesMaster`` (exported once, as a series), so exporting the instances
#: too would duplicate every recurring meeting — the default skips them.
STANDALONE_EVENT_TYPES = ("singleInstance", "seriesMaster")

#: Graph ``showAs`` → iCalendar ``TRANSP``: only a free event is transparent.
_TRANSP = {"free": "TRANSPARENT"}

#: Graph ``showAs`` → iCalendar ``STATUS``; only a tentative event carries one.
_STATUS = {"tentative": "TENTATIVE"}

#: Graph ``sensitivity`` → iCalendar ``CLASS``.
_CLASS = {
    "normal": "PUBLIC",
    "personal": "PRIVATE",
    "private": "PRIVATE",
    "confidential": "CONFIDENTIAL",
}

#: Graph ``importance`` → iCalendar ``PRIORITY`` (1 highest, 5 normal, 9 lowest).
_PRIORITY = {"high": "1", "normal": "5", "low": "9"}

#: Graph attendee ``type`` → iCalendar ``ROLE``.
_ROLE = {"required": "REQ-PARTICIPANT", "optional": "OPT-PARTICIPANT", "resource": "NON-PARTICIPANT"}

#: Graph attendee ``status.response`` → iCalendar ``PARTSTAT``.
_PARTSTAT = {
    "none": "NEEDS-ACTION",
    "organizer": "ACCEPTED",
    "tentativelyAccepted": "TENTATIVE",
    "accepted": "ACCEPTED",
    "declined": "DECLINED",
    "notResponded": "NEEDS-ACTION",
}

#: Graph ``dayOfWeek`` → RFC 5545 weekday abbreviation.
_DAY_CODES = {
    "sunday": "SU",
    "monday": "MO",
    "tuesday": "TU",
    "wednesday": "WE",
    "thursday": "TH",
    "friday": "FR",
    "saturday": "SA",
}

#: Graph ``pattern.index`` → RFC 5545 ``BYDAY`` ordinal prefix.
_INDEX_CODES = {"first": "1", "second": "2", "third": "3", "fourth": "4", "last": "-1"}

#: Graph ``pattern.type`` → the RFC 5545 ``FREQ`` that pattern expresses.
_FREQUENCY = {
    "daily": "DAILY",
    "weekly": "WEEKLY",
    "absoluteMonthly": "MONTHLY",
    "relativeMonthly": "MONTHLY",
    "absoluteYearly": "YEARLY",
    "relativeYearly": "YEARLY",
}

#: RFC 5545 §3.1 caps a content line at 75 octets; a continuation starts with a space.
MAX_LINE_OCTETS = 75

#: A Graph ``dateTime`` is a wall-clock literal with a 7-digit fraction and no
#: offset (``2026-03-02T09:00:00.0000000``); the zone rides in ``timeZone``.
_FRACTION = re.compile(r"\.\d+")
_COMPACT = re.compile(r"[^0-9]")


@dataclass
class CalendarExportOptions:
    """What a calendar export includes."""

    #: Name of the top folder in the export tree (``None`` uses the calendar's own
    #: display name, slugified). Set it to keep a stable root across renames.
    root_name: str | None = None
    #: Export the individual occurrences/exceptions of a recurring event as well as
    #: the series. Off by default: a series already carries its pattern, and each
    #: instance copied as a standalone event would show up twice in the target.
    include_recurring_instances: bool = False
    #: Export cancelled events. Off by default: a cancelled event is a tombstone,
    #: and the import creates live events, so replaying one would resurrect a
    #: meeting the user cancelled.
    include_cancelled: bool = False
    #: Extra Graph event properties to record in the sidecar (camelCase names).
    extra_properties: list[str] = field(default_factory=list)


def event_key(event) -> str:
    """The identity an export is keyed by: the Graph event id.

    Deliberately not ``iCalUid``: Exchange assigns one to a *meeting* but not to a
    plain appointment (measured — an event created through the API comes back with
    ``iCalUid: null`` even on a later read), so keying on it would let a re-run see
    the same event under a new identity and write a second copy. The Graph id is
    stable for the event's life in its calendar. ``iCalUid`` is still what other
    calendar clients match on, so it rides in the sidecar and becomes the ``.ics``
    ``UID`` when present.
    """
    return str(event.id or event.get_property("iCalUid") or "")


def event_dest_path(event, calendar_path: str) -> str:
    """The export path for an event: ``<calendar>/<date>_<slug>_<id digest>.ics``.

    Deterministic for a given event, so a re-run finds the file it wrote. The date
    is the event's start date — a calendar sorted by filename reads
    chronologically — and the digest of :func:`event_key` keeps same-titled events
    on the same day apart.
    """
    start = _started(event)
    stamp = start.strftime("%Y-%m-%d") if start else ""
    digest = hashlib.sha1(event_key(event).encode("utf-8")).hexdigest()[:8]
    stem = "_".join(part for part in (stamp, mail_slug(event.get_property("subject")), digest) if part)
    name = f"{stem}.ics"
    return f"{calendar_path}/{name}" if calendar_path else name


def _started(event) -> datetime | None:
    """The event's start as a naive wall-clock datetime (its own zone), if set."""
    value = _as_dict(event.get_property("start")).get("dateTime")
    return _parse_graph_datetime(value)


def _parse_graph_datetime(value: Any) -> datetime | None:
    """Parse a Graph wall-clock literal, tolerating any fraction width (py3.8-safe)."""
    if not value:
        return None
    text = _FRACTION.sub("", str(value).strip())
    try:
        return datetime.strptime(text[:19], "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return None


def _as_dict(value: Any) -> dict[str, Any]:
    """A Graph nested value as a plain dict.

    A fetched event hands back *typed* ``ClientValue`` objects (``start`` is a
    ``DateTimeTimeZone``, ``body`` an ``ItemBody``), so the raw property bag is only
    reachable through ``to_json()`` — ``get_property`` returns the wrapper.
    """
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    to_json = getattr(value, "to_json", None)
    if callable(to_json):
        payload = to_json()
        if isinstance(payload, dict):
            return payload
    properties = getattr(value, "properties", None)
    return properties if isinstance(properties, dict) else {}


def _wire(value: Any) -> Any:
    """A Graph enum as the name the wire uses.

    The generated Outlook enums carry *numeric* values on v1.0 (``FreeBusyStatus``
    is ``'0'..'4'``) while the service speaks the member name, so ``.name`` is the
    wire form — ``str()`` or ``.value`` would record ``FullBusyStatus.tentative``.
    """
    return value.name if isinstance(value, Enum) else value


def _address(recipient: Any) -> dict[str, str | None]:
    """An event's organizer/attendee as ``{"name", "address"}``."""
    email_address = _as_dict(_as_dict(recipient).get("emailAddress"))
    return {"name": email_address.get("name"), "address": email_address.get("address")}


def event_envelope(
    event,
    calendar_path: str,
    extra_properties: list[str] | None = None,
    display_path: str | None = None,
) -> dict[str, Any]:
    """The sidecar record for an event: everything an import replays.

    All values are JSON-safe. ``start``/``end`` keep Graph's pair of wall-clock
    ``date_time`` and ``time_zone`` (the zone name is passed back verbatim on
    import, so no IANA/Windows conversion is needed); ``recurrence`` is Graph's
    own object, not an ``RRULE`` — the ICS writer renders an ``RRULE`` from it, but
    the import replays the object it can round-trip exactly.
    """
    body = _as_dict(event.get_property("body"))
    online = _as_dict(event.get_property("onlineMeeting"))
    locations = [_as_dict(item).get("displayName") for item in (event.get_property("locations") or [])]
    envelope: dict[str, Any] = {
        "graph_id": event.id,
        "ical_uid": event.get_property("iCalUid"),
        "calendar_path": calendar_path,
        "calendar_display_path": display_path or calendar_path,
        "subject": event.get_property("subject"),
        "body": {"content_type": body.get("contentType"), "content": body.get("content")},
        "start": _as_dict(event.get_property("start")),
        "end": _as_dict(event.get_property("end")),
        "is_all_day": bool(event.get_property("isAllDay")),
        "is_cancelled": bool(event.get_property("isCancelled")),
        "show_as": _wire(event.get_property("showAs")),
        "sensitivity": _wire(event.get_property("sensitivity")),
        "importance": _wire(event.get_property("importance")),
        "location": _as_dict(event.get_property("location")).get("displayName"),
        "locations": [name for name in locations if name],
        "organizer": _address(event.get_property("organizer")),
        "attendees": [
            {**_address(attendee), "type": _as_dict(attendee).get("type"), "response": _response(attendee)}
            for attendee in (event.get_property("attendees") or [])
        ],
        "categories": list(event.get_property("categories") or []),
        "is_reminder_on": bool(event.get_property("isReminderOn")),
        "reminder_minutes": event.get_property("reminderMinutesBeforeStart"),
        "created": iso_or_none(event.get_property("createdDateTime")),
        "modified": iso_or_none(event.get_property("lastModifiedDateTime")),
        "type": _wire(event.get_property("type")),
        "series_master_id": event.get_property("seriesMasterId"),
        "recurrence": event.get_property("recurrence"),
        "is_online_meeting": bool(event.get_property("isOnlineMeeting")),
        "online_meeting_provider": event.get_property("onlineMeetingProvider"),
        "join_url": online.get("joinUrl"),
        "has_attachments": bool(event.get_property("hasAttachments")),
        "web_link": event.get_property("webLink"),
        "ics_path": event_dest_path(event, calendar_path),
    }
    for name in extra_properties or []:
        envelope[name] = event.get_property(name)
    return envelope


def _response(attendee: Any) -> str | None:
    """An attendee's response state (``status.response``), as Graph spells it."""
    return _as_dict(_as_dict(attendee).get("status")).get("response")


def _escape(text: Any) -> str:
    """Escape an iCalendar TEXT value (RFC 5545 §3.3.11)."""
    if text is None:
        return ""
    value = str(text)
    value = value.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,")
    return value.replace("\r\n", "\\n").replace("\n", "\\n").replace("\r", "\\n")


def _fold(line: str) -> str:
    """Fold a content line at 75 octets, continuing with a leading space (RFC 5545 §3.1)."""
    encoded = line.encode("utf-8")
    if len(encoded) <= MAX_LINE_OCTETS:
        return line
    limit = MAX_LINE_OCTETS - 1  # the continuation's leading space is part of its octets
    chunks, current, size = [], [], 0
    for char in line:
        width = len(char.encode("utf-8"))
        if size + width > limit:
            chunks.append("".join(current))
            current, size = [char], width
        else:
            current.append(char)
            size += width
    chunks.append("".join(current))
    return "\r\n ".join(chunks)


def _datetime_line(name: str, value: dict[str, Any], is_all_day: bool) -> str | None:
    """A ``DTSTART``/``DTEND`` line: a date for an all-day event, else zoned or UTC."""
    moment = _parse_graph_datetime(value.get("dateTime"))
    if moment is None:
        return None
    if is_all_day:
        return f"{name};VALUE=DATE:{moment.strftime('%Y%m%d')}"
    zone = (value.get("timeZone") or "UTC").strip()
    if zone.upper() == "UTC":
        return f"{name}:{moment.strftime('%Y%m%dT%H%M%S')}Z"
    return f"{name};TZID={zone}:{moment.strftime('%Y%m%dT%H%M%S')}"


def _day_codes(days: list[Any] | None) -> str:
    """``["monday", "wednesday"]`` -> ``MO,WE`` (in the week order Graph returned)."""
    return ",".join(_DAY_CODES[day] for day in (days or []) if day in _DAY_CODES)


def _rrule(recurrence: Any) -> str | None:
    """Render Graph's recurrence object as an RFC 5545 ``RRULE`` value.

    Returns ``None`` for a shape this writer does not express (or when there is no
    recurrence); the sidecar keeps the object either way, so a lost ``RRULE`` costs
    a calendar's interop, never the import.
    """
    pattern = _as_dict(_as_dict(recurrence).get("pattern"))
    window = _as_dict(_as_dict(recurrence).get("range"))
    frequency = _FREQUENCY.get(str(pattern.get("type") or ""))
    if not frequency:
        return None
    parts = [f"FREQ={frequency}"]
    interval = pattern.get("interval")
    if isinstance(interval, int) and interval > 1:
        parts.append(f"INTERVAL={interval}")
    if frequency == "WEEKLY" and _day_codes(pattern.get("daysOfWeek")):
        parts.append(f"BYDAY={_day_codes(pattern.get('daysOfWeek'))}")
    elif frequency == "MONTHLY":
        if pattern.get("dayOfMonth"):
            parts.append(f"BYMONTHDAY={pattern['dayOfMonth']}")
        elif _day_codes(pattern.get("daysOfWeek")):
            index = _INDEX_CODES.get(str(pattern.get("index") or ""))
            codes = _day_codes(pattern.get("daysOfWeek")).split(",")
            parts.append(f"BYDAY={','.join((index or '') + code for code in codes)}")
    elif frequency == "YEARLY":
        if pattern.get("month"):
            parts.append(f"BYMONTH={pattern['month']}")
        if pattern.get("dayOfMonth"):
            parts.append(f"BYMONTHDAY={pattern['dayOfMonth']}")
        elif _day_codes(pattern.get("daysOfWeek")):
            index = _INDEX_CODES.get(str(pattern.get("index") or ""))
            codes = _day_codes(pattern.get("daysOfWeek")).split(",")
            parts.append(f"BYDAY={','.join((index or '') + code for code in codes)}")
    occurrences = window.get("numberOfOccurrences")
    if window.get("type") == "numbered" and isinstance(occurrences, int) and occurrences > 0:
        parts.append(f"COUNT={occurrences}")
    elif window.get("type") == "endDate":
        until = _parse_graph_datetime(window.get("endDate"))
        if until is not None:
            parts.append(f"UNTIL={until.strftime('%Y%m%dT%H%M%S')}Z")
    return ";".join(parts)


def _attendee_line(attendee: dict[str, Any]) -> str | None:
    """One ``ATTENDEE`` line, skipping an attendee without an address."""
    address = attendee.get("address")
    if not address:
        return None
    parameters = []
    if attendee.get("name"):
        parameters.append(f'CN="{attendee["name"]}"')
    role = _ROLE.get(str(attendee.get("type") or "required"))
    if role:
        parameters.append(f"ROLE={role}")
    status = _PARTSTAT.get(str(attendee.get("response") or "none"))
    if status:
        parameters.append(f"PARTSTAT={status}")
    parameters.append("RSVP=TRUE")
    return f"ATTENDEE;{';'.join(parameters)}:mailto:{address}"


def event_ics(envelope: dict[str, Any]) -> bytes:
    """Render a sidecar record as an ``.ics`` document (CRLF, folded, UTF-8).

    The output depends only on the record — ``DTSTAMP`` is the event's own
    last-modified time, never the export's — so re-exporting an unchanged event
    produces identical bytes and a byte checksum verifies the tree.
    """
    is_all_day = bool(envelope.get("is_all_day"))
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//office365-rest-python-client//migration//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "BEGIN:VEVENT",
    ]
    uid = envelope.get("ical_uid") or envelope.get("graph_id") or ""
    lines.append(f"UID:{_escape(uid)}")
    stamp = _parse_graph_datetime(envelope.get("modified")) or _parse_graph_datetime(
        (envelope.get("start") or {}).get("dateTime")
    )
    if stamp is not None:
        lines.append(f"DTSTAMP:{stamp.strftime('%Y%m%dT%H%M%S')}Z")
    for name, key in (("DTSTART", "start"), ("DTEND", "end")):
        line = _datetime_line(name, _as_dict(envelope.get(key)), is_all_day)
        if line:
            lines.append(line)
    lines.append(f"SUMMARY:{_escape(envelope.get('subject'))}")
    location = envelope.get("location")
    if location:
        lines.append(f"LOCATION:{_escape(location)}")
    body = _as_dict(envelope.get("body"))
    content = body.get("content")
    if content:
        if body.get("content_type") == "html":
            # iCalendar's DESCRIPTION is TEXT; HTML rides in the standard X-ALT-DESC.
            lines.append(f"X-ALT-DESC;FMTTYPE=text/html:{_escape(content)}")
        else:
            lines.append(f"DESCRIPTION:{_escape(content)}")
    categories = envelope.get("categories") or []
    if categories:
        lines.append(f"CATEGORIES:{','.join(_escape(item) for item in categories)}")
    mapping = (
        ("CLASS", _CLASS.get(str(envelope.get("sensitivity") or ""))),
        ("PRIORITY", _PRIORITY.get(str(envelope.get("importance") or ""))),
        ("STATUS", _STATUS.get(str(envelope.get("show_as") or ""))),
        ("TRANSP", _TRANSP.get(str(envelope.get("show_as") or ""))),
    )
    lines.extend(f"{name}:{value}" for name, value in mapping if value)
    organizer = _as_dict(envelope.get("organizer"))
    if organizer.get("address"):
        name = f'CN="{organizer["name"]}"' if organizer.get("name") else ""
        lines.append(f"ORGANIZER{';' + name if name else ''}:mailto:{organizer['address']}")
    lines.extend(line for line in (_attendee_line(item) for item in envelope.get("attendees") or []) if line)
    rule = _rrule(envelope.get("recurrence"))
    if rule:
        lines.append(f"RRULE:{rule}")
    if envelope.get("join_url"):
        lines.append(f"X-MICROSOFT-SKYPETEAMSMEETINGURL:{_escape(envelope['join_url'])}")
    minutes = envelope.get("reminder_minutes")
    if envelope.get("is_reminder_on") and isinstance(minutes, int) and minutes > 0:
        lines.extend(
            [
                "BEGIN:VALARM",
                "ACTION:DISPLAY",
                f"TRIGGER:-PT{minutes}M",
                f"DESCRIPTION:{_escape(envelope.get('subject') or 'Reminder')}",
                "END:VALARM",
            ]
        )
    lines.extend(["END:VEVENT", "END:VCALENDAR", ""])
    return "\r\n".join(_fold(line) for line in lines).encode("utf-8")


__all__ = [
    "EVENT_COLUMNS",
    "STANDALONE_EVENT_TYPES",
    "CalendarExportOptions",
    "event_dest_path",
    "event_envelope",
    "event_ics",
    "event_key",
]
