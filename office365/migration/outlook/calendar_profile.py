"""The calendar's vocabulary as data: Graph's words, and the tokens they become.

Nothing here decides *when* a token is written — that is the codec's job — and nothing
here knows about a client: these are tables, so the answer to "what does a
tentatively-accepted attendee look like in an ``.ics``" is a row, not a branch.

:class:`IcsProfile` is the ``.ics`` spelling: one table per generated Graph enum the
writer speaks. Each is checked against its enum by ``tests/unit/test_calendar_profile.py``
— a row naming a member the model does not declare fails the suite, because a token for
a word the service never sends is a lie. ``transp`` and ``status`` are deliberately
*partial*: a busy event carries no ``TRANSP`` and an accepted one no ``STATUS``, since
those are what a reader assumes by default, so their incompleteness is the spelling
rather than an omission.

:data:`COMPARED` is the *comparison* spelling: one :class:`FieldRule` per sidecar field a
digest takes part in, carrying the normalisation Exchange forces on a round trip (a body
comes back re-wrapped in HTML, a wall clock comes back with a different fraction of a
second) and the import option that can decline to restore the field at all. A field the
sidecar gains is therefore a row here, not a line in a hand-built dict.

The envelope these rules read is the event as the model serializes it
(``Event.to_json()``), so the keys are Graph's own — ``isAllDay``, ``showAs``, a
``{"displayName": …}`` location, an attendee's ``emailAddress`` and ``status.response``.
Nothing here re-spells them.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from datetime import datetime
from types import MappingProxyType
from typing import Any, Callable, Mapping, Sequence

from office365.runtime.converters.scalars import parse_datetime


@dataclass(frozen=True)
class IcsProfile:
    """How one calendar dialect spells Graph's words — RFC 5545 names, by table."""

    #: Graph ``showAs`` → ``TRANSP``: only a free event is transparent.
    transp: Mapping[str, str]
    #: Graph ``showAs`` → ``STATUS``: only a tentative event carries one.
    status: Mapping[str, str]
    #: Graph ``sensitivity`` → ``CLASS``.
    classification: Mapping[str, str]
    #: Graph ``importance`` → ``PRIORITY`` (1 highest, 5 normal, 9 lowest).
    priority: Mapping[str, str]
    #: Graph attendee ``type`` → ``ROLE``.
    role: Mapping[str, str]
    #: Graph attendee ``status.response`` → ``PARTSTAT``.
    partstat: Mapping[str, str]
    #: Graph ``dayOfWeek`` → RFC 5545 weekday abbreviation.
    weekdays: Mapping[str, str]
    #: Graph ``pattern.index`` → the ordinal prefix of a ``BYDAY`` value.
    week_index: Mapping[str, str]
    #: Graph ``pattern.type`` → the ``FREQ`` that pattern expresses.
    frequency: Mapping[str, str]
    #: Graph body ``contentType`` → the property the text is written to.
    body_field: Mapping[str, str]


#: The dialect this writer speaks. A second dialect — ``METHOD:REQUEST`` for an
#: invitation, a different ``PARTSTAT`` default — is another row, not another writer.
ICALENDAR = IcsProfile(
    transp=MappingProxyType({"free": "TRANSPARENT"}),
    status=MappingProxyType({"tentative": "TENTATIVE"}),
    classification=MappingProxyType(
        {"normal": "PUBLIC", "personal": "PRIVATE", "private": "PRIVATE", "confidential": "CONFIDENTIAL"}
    ),
    priority=MappingProxyType({"high": "1", "normal": "5", "low": "9"}),
    role=MappingProxyType({"required": "REQ-PARTICIPANT", "optional": "OPT-PARTICIPANT", "resource": "NON-PARTICIPANT"}),
    partstat=MappingProxyType(
        {
            "none": "NEEDS-ACTION",
            "organizer": "ACCEPTED",
            "tentativelyAccepted": "TENTATIVE",
            "accepted": "ACCEPTED",
            "declined": "DECLINED",
            "notResponded": "NEEDS-ACTION",
        }
    ),
    weekdays=MappingProxyType(
        {
            "sunday": "SU",
            "monday": "MO",
            "tuesday": "TU",
            "wednesday": "WE",
            "thursday": "TH",
            "friday": "FR",
            "saturday": "SA",
        }
    ),
    week_index=MappingProxyType({"first": "1", "second": "2", "third": "3", "fourth": "4", "last": "-1"}),
    frequency=MappingProxyType(
        {
            "daily": "DAILY",
            "weekly": "WEEKLY",
            "absoluteMonthly": "MONTHLY",
            "relativeMonthly": "MONTHLY",
            "absoluteYearly": "YEARLY",
            "relativeYearly": "YEARLY",
        }
    ),
    # iCalendar's ``DESCRIPTION`` is TEXT; HTML rides in the standard ``X-ALT-DESC``,
    # which a client that does not understand it still shows as a plain description.
    body_field=MappingProxyType({"html": "X-ALT-DESC;FMTTYPE=text/html", "text": "DESCRIPTION"}),
)


def parse_wall_clock(value: Any) -> datetime | None:
    """A Graph date-time literal as a *naive wall clock*, or ``None``.

    The parsing itself is the library's (``parse_datetime`` normalises any
    fractional-second width — Graph sends seven digits and ``%f`` reads six). What is
    decided here is this package's own semantics: values are compared and formatted as
    wall clocks (the zone travels separately in ``timeZone``), so an offset is dropped,
    and a date-only literal — which a recurrence ``endDate`` is — is not a moment.
    """
    text = str(value or "").strip()
    if "T" not in text:
        return None
    parsed = parse_datetime(text)
    return parsed.replace(tzinfo=None) if parsed else None


#: Markup whose text is not content, and comments — dropped before a body is reduced
#: to text. Exchange wraps every body it accepts in its own ``<html><head>…<style>…``.
_MARKUP_BLOCK = re.compile(r"<(head|style|script)\b.*?</\1\s*>", re.IGNORECASE | re.DOTALL)
_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
_TAG = re.compile(r"<[^>]+>")
_SPACE = re.compile(r"\s+")


def text(value: Any) -> str:
    """A sidecar value as the comparable text an empty value and ``None`` share."""
    return str(value or "")


def wall_clock(pair: Any) -> tuple[str | None, str | None]:
    """A Graph ``{dateTime, timeZone}`` pair as a comparable ``(wall clock, zone)``.

    Graph varies the fractional-second width between what is sent and what comes back,
    so the fraction is dropped rather than compared.
    """
    moment = pair or {}
    parsed = parse_wall_clock(moment.get("dateTime"))
    zone = moment.get("timeZone")
    return (parsed.strftime("%Y-%m-%dT%H:%M:%S") if parsed else None, str(zone) if zone else None)


def names(value: Sequence[Any] | None) -> list[str]:
    """A label list a service keeps unordered compares as a sorted set, empties dropped."""
    return sorted(str(name) for name in value or [] if name)


def display_name(value: Mapping[str, Any] | None) -> str:
    """A Graph ``{"displayName": …}`` object as the text it carries (a location)."""
    return text((value or {}).get("displayName"))


def display_names(value: Sequence[Mapping[str, Any]] | None) -> list[str]:
    """A list of such objects, ordered, the nameless dropped."""
    return sorted(name for name in (display_name(item) for item in value or []) if name)


def _email_address(attendee: Mapping[str, Any]) -> Mapping[str, Any]:
    """The address part of an attendee/recipient, which is where a person is."""
    return attendee.get("emailAddress") or {}


def attendee_pairs(value: Sequence[Mapping[str, Any]] | None) -> list[tuple[str, str]]:
    """An attendee list as ``(address, type)``: an entry without an address is nobody."""
    return sorted(
        (str(_email_address(item).get("address") or "").lower(), str(item.get("type") or "required"))
        for item in value or []
        if _email_address(item).get("address")
    )


def body_text(value: Any) -> str:
    """A body reduced to its text, for comparison only.

    Exchange re-serializes every body it accepts: a plain-text body comes back wrapped
    in HTML, and an HTML body gains a ``<head>`` with a generated ``<style>`` block.
    The markup is therefore not comparable — the text is.
    """
    content = (value or {}).get("content")
    if not content:
        return ""
    stripped = _COMMENT.sub("", str(content))
    stripped = _MARKUP_BLOCK.sub("", stripped)
    stripped = _TAG.sub(" ", stripped)
    return _SPACE.sub(" ", html.unescape(stripped)).strip()


@dataclass(frozen=True)
class FieldRule:
    """One sidecar field as a digest compares it.

    ``gate`` names the :class:`CalendarImportOptions` attribute that decides whether an
    import restores the field at all: a source and a target of one job must agree on the
    options, so a field the import declines to replay stays out of the digest that
    verifies the replay.
    """

    #: The key this field takes in the canonical form.
    key: str
    #: The sidecar envelope → the comparable value.
    normalise: Callable[[Mapping[str, Any]], Any]
    #: The import option that decides whether the field is restored, if any.
    gate: str | None = None


#: Every sidecar field a digest compares, in canonical order. The sidecar's own
#: bookkeeping (the Graph id, the ``.ics`` path, the calendar it came from) is absent by
#: construction: it is provenance, not content, and an import never replays it.
COMPARED: tuple[FieldRule, ...] = (
    FieldRule("subject", lambda envelope: text(envelope.get("subject"))),
    FieldRule("start", lambda envelope: wall_clock(envelope.get("start"))),
    FieldRule("end", lambda envelope: wall_clock(envelope.get("end"))),
    FieldRule("all_day", lambda envelope: bool(envelope.get("isAllDay"))),
    FieldRule("location", lambda envelope: display_name(envelope.get("location"))),
    FieldRule("locations", lambda envelope: display_names(envelope.get("locations"))),
    FieldRule("show_as", lambda envelope: envelope.get("showAs")),
    FieldRule("sensitivity", lambda envelope: envelope.get("sensitivity")),
    FieldRule("importance", lambda envelope: envelope.get("importance")),
    FieldRule(
        "reminder",
        lambda envelope: (bool(envelope.get("isReminderOn")), envelope.get("reminderMinutesBeforeStart") or 0),
    ),
    FieldRule("recurrence", lambda envelope: envelope.get("recurrence")),
    FieldRule("body", lambda envelope: body_text(envelope.get("body"))),
    FieldRule("attendees", lambda envelope: attendee_pairs(envelope.get("attendees")), gate="restore_attendees"),
    FieldRule("categories", lambda envelope: names(envelope.get("categories")), gate="restore_categories"),
)


__all__ = [
    "COMPARED",
    "ICALENDAR",
    "FieldRule",
    "IcsProfile",
    "attendee_pairs",
    "body_text",
    "display_name",
    "display_names",
    "names",
    "parse_wall_clock",
    "text",
    "wall_clock",
]
