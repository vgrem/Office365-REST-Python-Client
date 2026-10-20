from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import overload

from office365.runtime.client_value import ClientValue
from office365.runtime.converters.scalars import parse_datetime


def _zone_name(tzinfo: object) -> str | None:
    """The name a ``tzinfo`` carries, if it has one (``zoneinfo`` key, ``pytz`` zone)."""
    for attribute in ("key", "zone"):
        name = getattr(tzinfo, attribute, None)
        if isinstance(name, str) and name:
            return name
    return None


def _wall_clock(value: datetime) -> str:
    """Graph's literal: seven fractional digits, no offset."""
    return f"{value:%Y-%m-%dT%H:%M:%S}.{value.microsecond:06d}0"


@dataclass
class DateTimeTimeZone(ClientValue):
    """Describes the date, time, and time zone of a point in time.

    Fields:
        dateTime (str | None): A single point of time in a combined date and time representation ({date}T{time};
            for example, 2017-08-29T04:00:00.0000000).
        timeZone (str | None): Represents a time zone, for example, "Pacific Standard Time" or "Europe/Kyiv".
    """

    dateTime: str | None = None
    timeZone: str | None = None

    def __repr__(self):
        return f"DateTimeTimeZone(dateTime={self.dateTime!r}, timeZone={self.timeZone!r})"

    def __str__(self):
        if self.dateTime and self.timeZone:
            return f"{self.dateTime} ({self.timeZone})"
        return self.dateTime or ""

    @overload
    @staticmethod
    def parse(value: None) -> None: ...

    @overload
    @staticmethod
    def parse(value: DateTimeTimeZone | datetime | dict | str) -> DateTimeTimeZone: ...

    @staticmethod
    def parse(value: DateTimeTimeZone | datetime | dict | str | None) -> DateTimeTimeZone | None:
        """Read any reasonable date-time input as a Graph ``DateTimeTimeZone``.

        Args:
            value: a ``DateTimeTimeZone`` or a Graph-spelled ``dict`` (both returned
                as a value), a date-time ``str``, a ``datetime``, or ``None``.

        A ``datetime`` keeps its meaning: an aware one keeps its own zone — its wall
        clock and the name of its ``tzinfo`` — and one with an unnamed offset is
        converted to UTC so the instant survives. A naive one is read as UTC, which
        is what this client has always done and what Graph documents as the default.

        The result is the wire form Graph documents — a wall clock with a
        seven-digit fraction and the zone named *separately*. The offset is never
        appended to ``dateTime``: Graph reads that field as a wall clock, so an
        offset there is a second, competing zone.
        """
        if value is None or isinstance(value, DateTimeTimeZone):
            return value
        if isinstance(value, dict):
            return DateTimeTimeZone(dateTime=value.get("dateTime"), timeZone=value.get("timeZone"))
        if isinstance(value, str):
            return DateTimeTimeZone(dateTime=value)
        if not isinstance(value, datetime):
            raise TypeError(f"expected a datetime, a graph dict, a string or a DateTimeTimeZone, got {type(value)}")
        zone = _zone_name(value.tzinfo)
        if value.tzinfo is not None and zone is None:
            value = value.astimezone(timezone.utc)
        return DateTimeTimeZone(dateTime=_wall_clock(value), timeZone=zone or "UTC")

    def as_datetime(self) -> datetime | None:
        """The wall clock ``dateTime`` names, or ``None`` when it names nothing.

        Deliberately naive. Graph names a zone — "W. Europe Standard Time",
        "Europe/Kyiv" — and turning a *name* into an offset needs a time-zone
        database that this runtime does not ship for the Windows spellings, so the
        name is left where the service put it, on :attr:`timeZone`, rather than
        guessed into an offset that would silently be wrong for half the year.
        """
        if not self.dateTime:
            return None
        parsed = parse_datetime(str(self.dateTime))
        return parsed.replace(tzinfo=None) if parsed else None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DateTimeTimeZone"
