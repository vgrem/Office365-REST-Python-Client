"""The ``.ics`` codec: one sidecar record, one iCalendar document, and back again.

The codec owns RFC 5545 and nothing else: escaping, folding, the line-per-field layout
of a ``VEVENT``, and the ``RRULE`` an event's recurrence object becomes. *Which* token a
Graph value is spelled with is a table in :mod:`calendar_profile`, so this module has no
vocabulary of its own — every ``CLASS``/``PRIORITY``/``TRANSP``/``PARTSTAT`` it writes is
a lookup.

The envelope it reads is the event as the model serializes it — ``Event.to_json()``
plus provenance — so the keys are Graph's own (``isAllDay``, ``showAs``,
``attendees[].status.response``); this module re-spells none of them.

The output depends only on the record (``DTSTAMP`` is the event's own last-modified
time, never the export's), so re-exporting an unchanged event produces identical bytes
and a byte checksum verifies the tree.
"""

from __future__ import annotations

from typing import Any, Mapping

from office365.migration.outlook.calendar_profile import ICALENDAR, IcsProfile, display_name, parse_wall_clock

#: RFC 5545 §3.1 caps a content line at 75 octets; a continuation starts with a space.
MAX_LINE_OCTETS = 75


def escape_text(value: Any) -> str:
    """Escape an iCalendar TEXT value (RFC 5545 §3.3.11)."""
    if value is None:
        return ""
    text = str(value)
    text = text.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,")
    return text.replace("\r\n", "\\n").replace("\n", "\\n").replace("\r", "\\n")


def fold_line(line: str) -> str:
    """Fold a content line at 75 octets, continuing with a leading space (RFC 5545 §3.1)."""
    encoded = line.encode("utf-8")
    if len(encoded) <= MAX_LINE_OCTETS:
        return line
    limit = MAX_LINE_OCTETS - 1  # the continuation's leading space is part of its octets
    chunks: list[str] = []
    current: list[str] = []
    size = 0
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


def date_time_line(name: str, value: Mapping[str, Any], is_all_day: bool) -> str | None:
    """A ``DTSTART``/``DTEND`` line: a date for an all-day event, else zoned or UTC."""
    moment = parse_wall_clock(value.get("dateTime"))
    if moment is None:
        return None
    if is_all_day:
        return f"{name};VALUE=DATE:{moment.strftime('%Y%m%d')}"
    zone = str(value.get("timeZone") or "UTC").strip()
    if zone.upper() == "UTC":
        return f"{name}:{moment.strftime('%Y%m%dT%H%M%S')}Z"
    return f"{name};TZID={zone}:{moment.strftime('%Y%m%dT%H%M%S')}"


def day_codes(days: list[Any] | None, profile: IcsProfile = ICALENDAR) -> str:
    """``["monday", "wednesday"]`` -> ``MO,WE`` (in the week order Graph returned)."""
    return ",".join(profile.weekdays[day] for day in days or [] if day in profile.weekdays)


def rrule(recurrence: Any, profile: IcsProfile = ICALENDAR) -> str | None:
    """Render Graph's recurrence object as an RFC 5545 ``RRULE`` value.

    Returns ``None`` for a shape this writer does not express (or when there is no
    recurrence); the sidecar keeps the object either way, so a lost ``RRULE`` costs a
    calendar's interop, never the import.
    """
    pattern = (recurrence or {}).get("pattern") or {}
    window = (recurrence or {}).get("range") or {}
    frequency = profile.frequency.get(str(pattern.get("type") or ""))
    if not frequency:
        return None
    parts = [f"FREQ={frequency}"]
    interval = pattern.get("interval")
    if isinstance(interval, int) and interval > 1:
        parts.append(f"INTERVAL={interval}")
    days = day_codes(pattern.get("daysOfWeek"), profile)
    if frequency == "WEEKLY" and days:
        parts.append(f"BYDAY={days}")
    elif frequency in ("MONTHLY", "YEARLY"):
        if frequency == "YEARLY" and pattern.get("month"):
            parts.append(f"BYMONTH={pattern['month']}")
        if pattern.get("dayOfMonth"):
            parts.append(f"BYMONTHDAY={pattern['dayOfMonth']}")
        elif days:
            index = profile.week_index.get(str(pattern.get("index") or ""))
            parts.append(f"BYDAY={','.join((index or '') + code for code in days.split(','))}")
    occurrences = window.get("numberOfOccurrences")
    if window.get("type") == "numbered" and isinstance(occurrences, int) and occurrences > 0:
        parts.append(f"COUNT={occurrences}")
    elif window.get("type") == "endDate":
        until = parse_wall_clock(window.get("endDate"))
        if until is not None:
            parts.append(f"UNTIL={until.strftime('%Y%m%dT%H%M%S')}Z")
    return ";".join(parts)


def attendee_line(attendee: Mapping[str, Any], profile: IcsProfile = ICALENDAR) -> str | None:
    """One ``ATTENDEE`` line, skipping an attendee without an address."""
    person = attendee.get("emailAddress") or {}
    address = person.get("address")
    if not address:
        return None
    parameters = []
    if person.get("name"):
        parameters.append(f'CN="{person["name"]}"')
    role = profile.role.get(str(attendee.get("type") or "required"))
    if role:
        parameters.append(f"ROLE={role}")
    status = profile.partstat.get(str((attendee.get("status") or {}).get("response") or "none"))
    if status:
        parameters.append(f"PARTSTAT={status}")
    parameters.append("RSVP=TRUE")
    return f"ATTENDEE;{';'.join(parameters)}:mailto:{address}"


def encode(envelope: Mapping[str, Any], profile: IcsProfile = ICALENDAR) -> bytes:
    """Render a sidecar record as an ``.ics`` document (CRLF, folded, UTF-8)."""
    is_all_day = bool(envelope.get("isAllDay"))
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//office365-rest-python-client//migration//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "BEGIN:VEVENT",
    ]
    uid = envelope.get("iCalUId") or envelope.get("id") or ""
    lines.append(f"UID:{escape_text(uid)}")
    stamp = parse_wall_clock(envelope.get("lastModifiedDateTime")) or parse_wall_clock(
        (envelope.get("start") or {}).get("dateTime")
    )
    if stamp is not None:
        lines.append(f"DTSTAMP:{stamp.strftime('%Y%m%dT%H%M%S')}Z")
    for name, key in (("DTSTART", "start"), ("DTEND", "end")):
        line = date_time_line(name, envelope.get(key) or {}, is_all_day)
        if line:
            lines.append(line)
    lines.append(f"SUMMARY:{escape_text(envelope.get('subject'))}")
    if display_name(envelope.get("location")):
        lines.append(f"LOCATION:{escape_text(display_name(envelope.get('location')))}")
    body = envelope.get("body") or {}
    content = body.get("content")
    if content:
        field = profile.body_field.get(str(body.get("contentType") or "").lower(), "DESCRIPTION")
        lines.append(f"{field}:{escape_text(content)}")
    categories = envelope.get("categories") or []
    if categories:
        lines.append(f"CATEGORIES:{','.join(escape_text(item) for item in categories)}")
    show_as = str(envelope.get("showAs") or "")
    mapping = (
        ("CLASS", profile.classification.get(str(envelope.get("sensitivity") or ""))),
        ("PRIORITY", profile.priority.get(str(envelope.get("importance") or ""))),
        ("STATUS", profile.status.get(show_as)),
        ("TRANSP", profile.transp.get(show_as)),
    )
    lines.extend(f"{name}:{value}" for name, value in mapping if value)
    organizer = (envelope.get("organizer") or {}).get("emailAddress") or {}
    if organizer.get("address"):
        name = f'CN="{organizer["name"]}"' if organizer.get("name") else ""
        lines.append(f"ORGANIZER{';' + name if name else ''}:mailto:{organizer['address']}")
    lines.extend(line for line in (attendee_line(item, profile) for item in envelope.get("attendees") or []) if line)
    rule = rrule(envelope.get("recurrence"), profile)
    if rule:
        lines.append(f"RRULE:{rule}")
    join_url = (envelope.get("onlineMeeting") or {}).get("joinUrl")
    if join_url:
        lines.append(f"X-MICROSOFT-SKYPETEAMSMEETINGURL:{escape_text(join_url)}")
    minutes = envelope.get("reminderMinutesBeforeStart")
    if envelope.get("isReminderOn") and isinstance(minutes, int) and minutes > 0:
        lines.extend(
            [
                "BEGIN:VALARM",
                "ACTION:DISPLAY",
                f"TRIGGER:-PT{minutes}M",
                f"DESCRIPTION:{escape_text(envelope.get('subject') or 'Reminder')}",
                "END:VALARM",
            ]
        )
    lines.extend(["END:VEVENT", "END:VCALENDAR", ""])
    return "\r\n".join(fold_line(line) for line in lines).encode("utf-8")


__all__ = [
    "MAX_LINE_OCTETS",
    "attendee_line",
    "date_time_line",
    "day_codes",
    "encode",
    "escape_text",
    "fold_line",
    "rrule",
]
