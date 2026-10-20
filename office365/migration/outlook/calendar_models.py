"""Calendar model — the export projection, the ICS writer, and the import replay.

An exported event is two files: an ``.ics`` (the portable artefact — Outlook,
Google Calendar and Thunderbird all open it) and a JSON sidecar carrying what
iCalendar cannot express faithfully (Graph ids, the recurrence object Graph
normalises, the online-meeting provider, sensitivity/importance). The sidecar is
the import contract; the ``.ics`` is regenerated from it, so an export is
reproducible: the same event always produces the same bytes.

Unlike mail, this file is *built* rather than fetched, so a byte checksum is a
valid verification of an export: there is no server re-serialization in the
middle. An *import* is the other way round — Exchange re-serializes what it
accepts — so it is verified by a digest of the event's restorable fields
(:func:`event_digest`).
"""

from __future__ import annotations

import hashlib
import html
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from office365.migration.outlook.models import mail_slug
from office365.outlook.calendar.events.event import Event
from office365.runtime.converters.scalars import iso_or_none, parse_datetime
from office365.runtime.converters.value import serialize_value

#: Graph event properties an export reads: every column the model declares.
#: Derived rather than listed, so a $select cannot disagree with the getters that
#: consume it — the class of bug that produced ``iCalUid`` (one capital short of
#: the real ``iCalUId``, silently ``None``) is now unrepresentable. Navigation
#: properties are excluded by construction: ``$select`` rejects them.
EVENT_COLUMNS = Event.select_all()

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

#: Markup whose text is not content, and comments — dropped before a body is reduced
#: to text. Exchange wraps every body it accepts in its own ``<html><head>…<style>…``.
_MARKUP_BLOCK = re.compile(r"<(head|style|script)\b.*?</\1\s*>", re.IGNORECASE | re.DOTALL)
_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
_TAG = re.compile(r"<[^>]+>")
_SPACE = re.compile(r"\s+")


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

    Deliberately not ``iCalUId``: Exchange assigns one to a *meeting* but not to a
    plain appointment (measured — an event created through the API comes back with
    ``iCalUId: null`` even on a later read), so keying on it would let a re-run see
    the same event under a new identity and write a second copy. The Graph id is
    stable for the event's life in its calendar. ``iCalUId`` is still what other
    calendar clients match on, so it rides in the sidecar and becomes the ``.ics``
    ``UID`` when present.
    """
    return str(event.id or event.ical_uid or "")


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
    stem = "_".join(part for part in (stamp, mail_slug(event.subject), digest) if part)
    name = f"{stem}.ics"
    return f"{calendar_path}/{name}" if calendar_path else name


def _started(event) -> datetime | None:
    """The event's start as a naive wall-clock datetime (its own zone), if set."""
    value = _as_dict(event.start).get("dateTime")
    return _parse_graph_datetime(value)


def _parse_graph_datetime(value: Any) -> datetime | None:
    """A Graph date-time literal as a *naive wall clock*, or ``None``.

    The parsing itself is the library's (``parse_datetime`` normalises any
    fractional-second width — Graph sends seven digits and ``%f`` reads six). What is
    decided here is this module's own semantics: values are compared and formatted as
    wall clocks (the zone travels separately in ``timeZone``), so an offset is dropped,
    and a date-only literal — which a recurrence ``endDate`` is — is not a moment.
    """
    text = str(value or "").strip()
    if "T" not in text:
        return None
    parsed = parse_datetime(text)
    return parsed.replace(tzinfo=None) if parsed else None


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


def event_kind(event) -> str | None:
    """The wire name of an event's ``type``: ``singleInstance``, ``seriesMaster``, …

    The getter answers with the generated enum, whose members carry the CSDL ordinals
    (``EventType.singleInstance.value == "0"``) rather than what the service speaks;
    ``serialize_value`` is the library's answer to that — the member *name*.
    """
    return serialize_value(event.type_)


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
    body = _as_dict(event.body)
    online = _as_dict(event.online_meeting)
    locations = [_as_dict(item).get("displayName") for item in (event.locations or [])]
    envelope: dict[str, Any] = {
        "graph_id": event.id,
        "ical_uid": event.ical_uid,
        "calendar_path": calendar_path,
        "calendar_display_path": display_path or calendar_path,
        "subject": event.subject,
        "body": {"content_type": body.get("contentType"), "content": body.get("content")},
        "start": _as_dict(event.start),
        "end": _as_dict(event.end),
        "is_all_day": bool(event.is_all_day),
        "is_cancelled": bool(event.is_cancelled),
        "show_as": serialize_value(event.show_as),
        "sensitivity": serialize_value(event.sensitivity),
        "importance": serialize_value(event.importance),
        "location": _as_dict(event.location).get("displayName"),
        "locations": [name for name in locations if name],
        "organizer": _address(event.organizer),
        "attendees": [
            {**_address(attendee), "type": _as_dict(attendee).get("type"), "response": _response(attendee)}
            for attendee in (event.attendees or [])
        ],
        "categories": list(event.categories or []),
        "is_reminder_on": bool(event.is_reminder_on),
        "reminder_minutes": event.reminder_minutes_before_start,
        "created": iso_or_none(event.created_datetime),
        "modified": iso_or_none(event.last_modified_datetime),
        "type": event_kind(event),
        "series_master_id": event.series_master_id,
        # Graph's own object, flattened through ``to_json()``: the raw property is a
        # typed ``PatternedRecurrence``, and the sidecar is JSON — ``default=str``
        # would have written its ``repr``, which no import can read back.
        "recurrence": _as_dict(event.recurrence) or None,
        "is_online_meeting": bool(event.is_online_meeting),
        "online_meeting_provider": serialize_value(event.online_meeting_provider),
        "join_url": online.get("joinUrl"),
        "has_attachments": bool(event.has_attachments),
        "web_link": event.web_link,
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


@dataclass
class CalendarImportOptions:
    """What an import of an exported calendar restores.

    Pass the *same* options object to both adapters of an import job: the source
    computes the content digest of what the target promises to restore, so the two
    sides have to agree on the fields to be comparable (see :func:`event_digest`).
    """

    #: Re-add the attendee list. **Off by default**, because creating an event with
    #: attendees makes Exchange send an invitation to every one of them (measured:
    #: a copy lands in the organizer's Sent Items, and ``responseRequested: false``
    #: does not suppress it) — so a historical import would spam colleagues with
    #: meetings they already had. With it off the attendees stay in the sidecar and
    #: the run reports how many were dropped.
    restore_attendees: bool = False
    #: Re-apply the category labels.
    restore_categories: bool = True
    #: Give every created event a deterministic ``transactionId``, so two concurrent
    #: runs of the same import collide on the server rather than both writing.
    use_transaction_ids: bool = True


def event_dedup_key(envelope: dict[str, Any]) -> tuple[str, str | None, str | None]:
    """The key a target matches an existing event on: subject and start.

    A created event comes back with ``iCalUId: null`` and a fresh Graph id, so neither
    of the source's identities survives the import — subject plus wall clock (and the
    zone it is in) is what is left to recognise a re-run's own work by.
    """
    wall, zone = _wall(envelope.get("start"))
    return (str(envelope.get("subject") or ""), wall, zone)


def event_transaction_id(envelope: dict[str, Any]) -> str:
    """A deterministic ``transactionId`` for an exported event."""
    key = str(envelope.get("graph_id") or envelope.get("ical_uid") or envelope.get("ics_path") or "")
    return "mig-" + hashlib.sha1(key.encode("utf-8")).hexdigest()[:32]


def event_create_payload(
    envelope: dict[str, Any],
    options: CalendarImportOptions | None = None,
) -> dict[str, Any]:
    """The Graph ``POST /events`` body for a sidecar record.

    Returns Graph's own spelling, so the target can post it verbatim: sending the
    typed ``DateTimeTimeZone`` helper instead loses the zone (it comes back ``UTC``)
    and the ``transactionId``, and ``EventCollection.add()`` rejects a dict for
    ``start`` outright (both measured).

    ``start``/``end`` are the pair of wall clock and *Windows* zone name the export
    recorded, passed back unchanged — Exchange accepts its own names, so no
    IANA conversion is needed. Anything Exchange assigns itself (``iCalUId``, the
    organizer, attendee responses, ``created``/``modified``) is not sent.
    """
    options = options or CalendarImportOptions()
    start = _as_dict(envelope.get("start"))
    end = _as_dict(envelope.get("end"))
    if not start.get("dateTime") or not end.get("dateTime"):
        raise ValueError("the sidecar record has no start/end dateTime: an event cannot be created without a time range")
    payload: dict[str, Any] = {
        "subject": envelope.get("subject") or "",
        "start": {"dateTime": start["dateTime"], "timeZone": start.get("timeZone") or "UTC"},
        "end": {"dateTime": end["dateTime"], "timeZone": end.get("timeZone") or "UTC"},
    }
    body = _as_dict(envelope.get("body"))
    if body.get("content"):
        # Graph spells the content type as an enum; the sidecar keeps the wire name.
        is_html = str(body.get("content_type") or "").lower() == "html"
        payload["body"] = {"contentType": "HTML" if is_html else "Text", "content": body["content"]}
    if envelope.get("is_all_day"):
        payload["isAllDay"] = True
    if envelope.get("location"):
        payload["location"] = {"displayName": envelope["location"]}
    locations = [name for name in envelope.get("locations") or [] if name]
    if locations:
        payload["locations"] = [{"displayName": name} for name in locations]
    attendees = _attendee_payloads(envelope)
    if attendees and options.restore_attendees:
        payload["attendees"] = attendees
    categories = [name for name in envelope.get("categories") or [] if name]
    if categories and options.restore_categories:
        payload["categories"] = categories
    for name, key in (
        ("showAs", "show_as"),
        ("sensitivity", "sensitivity"),
        ("importance", "importance"),
    ):
        if envelope.get(key):
            payload[name] = envelope[key]
    if "is_reminder_on" in envelope:
        payload["isReminderOn"] = bool(envelope.get("is_reminder_on"))
        minutes = envelope.get("reminder_minutes")
        if payload["isReminderOn"] and isinstance(minutes, int) and minutes > 0:
            payload["reminderMinutesBeforeStart"] = minutes
    recurrence = envelope.get("recurrence")
    if isinstance(recurrence, str):
        raise ValueError(
            f"the sidecar records the recurrence as text ({recurrence[:60]!r}): it was written by a version of the"
            " exporter that serialised Graph's typed object with ``repr``, so the series cannot be replayed —"
            " re-export the calendar and import that tree"
        )
    if isinstance(recurrence, dict) and recurrence:
        payload["recurrence"] = recurrence
    if options.use_transaction_ids:
        payload["transactionId"] = event_transaction_id(envelope)
    return payload


def event_digest(envelope: dict[str, Any], options: CalendarImportOptions | None = None) -> str:
    """A digest of the fields an import restores, for verifying that it did.

    Not the ``.ics`` bytes: the other side of an import is Exchange, which
    re-serializes the body and assigns the meeting metadata, so the comparable
    artefact is the *event*. Two things are therefore outside the digest — everything
    the service owns (``iCalUId``, the organizer, attendee responses, created and
    modified times) and the body's markup (see :func:`_body_text`). Attendees and
    categories count only when ``options`` says the import restores them, which is
    why the source and the target of one job must share the options object.
    """
    options = options or CalendarImportOptions()
    canonical: dict[str, Any] = {
        "subject": envelope.get("subject") or "",
        "start": _wall(envelope.get("start")),
        "end": _wall(envelope.get("end")),
        "all_day": bool(envelope.get("is_all_day")),
        "location": envelope.get("location") or "",
        "locations": sorted(name for name in envelope.get("locations") or [] if name),
        "show_as": envelope.get("show_as"),
        "sensitivity": envelope.get("sensitivity"),
        "importance": envelope.get("importance"),
        "reminder": (bool(envelope.get("is_reminder_on")), envelope.get("reminder_minutes") or 0),
        "recurrence": envelope.get("recurrence"),
        "body": _body_text(envelope.get("body")),
    }
    if options.restore_attendees:
        canonical["attendees"] = sorted(
            (str(item.get("address") or "").lower(), str(item.get("type") or "required"))
            for item in _attendee_payloads(envelope)
        )
    if options.restore_categories:
        canonical["categories"] = sorted(str(name) for name in envelope.get("categories") or [])
    serialized = json.dumps(canonical, sort_keys=True, default=str)
    return hashlib.md5(serialized.encode("utf-8")).hexdigest()


def _attendee_payloads(envelope: dict[str, Any]) -> list[dict[str, Any]]:
    """The attendee list Graph accepts, from the addresses the sidecar recorded."""
    payloads: list[dict[str, Any]] = []
    for attendee in envelope.get("attendees") or []:
        address = _as_dict(attendee).get("address")
        if not address:
            continue
        item: dict[str, Any] = {"emailAddress": {"address": address}, "type": attendee.get("type") or "required"}
        if attendee.get("name"):
            item["emailAddress"]["name"] = attendee["name"]
        payloads.append(item)
    return payloads


def _wall(value: Any) -> tuple[str | None, str | None]:
    """A Graph ``{dateTime, timeZone}`` pair as a comparable ``(wall clock, zone)``.

    Graph varies the fractional-second width between what is sent and what comes
    back, so the fraction is dropped rather than compared.
    """
    moment = _as_dict(value)
    parsed = _parse_graph_datetime(moment.get("dateTime"))
    zone = moment.get("timeZone")
    return (parsed.strftime("%Y-%m-%dT%H:%M:%S") if parsed else None, str(zone) if zone else None)


def _body_text(body: Any) -> str:
    """A body reduced to its text, for comparison only.

    Exchange re-serializes every body it accepts: a plain-text body comes back wrapped
    in HTML, and an HTML body gains a ``<head>`` with a generated ``<style>`` block.
    The markup is therefore not comparable — the text is.
    """
    content = _as_dict(body).get("content")
    if not content:
        return ""
    text = _COMMENT.sub("", str(content))
    text = _MARKUP_BLOCK.sub("", text)
    text = _TAG.sub(" ", text)
    return _SPACE.sub(" ", html.unescape(text)).strip()


__all__ = [
    "EVENT_COLUMNS",
    "STANDALONE_EVENT_TYPES",
    "CalendarExportOptions",
    "CalendarImportOptions",
    "event_create_payload",
    "event_dedup_key",
    "event_dest_path",
    "event_digest",
    "event_envelope",
    "event_ics",
    "event_key",
    "event_transaction_id",
]
