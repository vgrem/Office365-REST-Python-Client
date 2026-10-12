"""Type-aware scalar value conversion (the "fields" layer of the conversion stack).

Each function converts a raw value (string, JSON scalar) into its typed form —
the deserialization half of the pipeline. ``serialize_value``/``deserialize_value``
in ``value.py`` build on these for object-level conversion.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional, Union

_TRUE_VALUES = {"true", "1", "yes", "y"}
_FALSE_VALUES = {"false", "0", "no", "n"}


def parse_enum(enum_type: type[Enum], value: str | int) -> Optional[Enum]:
    """Safely converts a value to the specified enum type.

    Args:
        enum_type: The Enum class to convert to
        value: The raw value to convert

    Returns:
        The enum member or None if conversion fails
    """
    try:
        return enum_type(value)
    except ValueError:
        try:
            return enum_type[str(value)]  # fallback: lookup by name
        except KeyError:
            return None


def parse_bool(value: Any) -> Any:
    """Convert a value to a boolean, falling back to the raw value when unrecognized.

    Args:
        value: The raw value to convert (e.g. a CSV cell)

    Returns:
        The parsed boolean, or the original value if it can't be parsed
    """
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in _TRUE_VALUES:
        return True
    if normalized in _FALSE_VALUES:
        return False
    return value


def parse_int(value: Any) -> Optional[int]:
    """Convert a value to an int, returning ``None`` when absent/invalid."""
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def try_int(value: Any) -> Any:
    """Convert a value to an int, falling back to the raw value on failure."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return value


def try_float(value: Any) -> Any:
    """Convert a value to a float, falling back to the raw value on failure."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return value


def utc_now_iso() -> str:
    """Current UTC time as an ISO-8601 string (second precision)."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def ensure_aware_utc(value: Optional[datetime]) -> Optional[datetime]:
    """Return ``value`` as a timezone-aware UTC datetime.

    Values created locally (for example when adding a credential) may carry no
    ``tzinfo``. Comparing such naive datetimes against :func:`datetime.now`
    (UTC) raises ``TypeError``; treat them as UTC instead.
    """
    if value is not None and value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def iso(value: Any) -> str:
    """ISO-8601 string for a datetime (second precision); ``""`` for ``None``."""
    if value is None:
        return ""
    return value.isoformat(timespec="seconds")


def iso_or_none(value: Any) -> Optional[str]:
    """ISO-8601 string for a datetime, or ``None`` when unset/absent.

    Treats ``datetime.min`` (the "not loaded" sentinel used by some SharePoint
    properties) as unset.
    """
    if value is None or value == datetime.min:
        return None
    return value.isoformat(timespec="seconds") if hasattr(value, "isoformat") else (str(value) or None)


def iso_z(value: Any) -> Optional[str]:
    """UTC ISO-8601 string with a ``Z`` suffix (second precision); ``None`` for ``None``.

    SharePoint and Microsoft Graph parse date-time strings on the wire as UTC
    with a trailing ``Z``; some endpoints (for example ``ShareLink``) reject a
    numeric offset such as ``+00:00`` as an invalid date. Naive datetimes are
    assumed to be UTC.
    """
    if value is None:
        return None
    if value.tzinfo is not None:
        value = value.astimezone(timezone.utc)
    return value.replace(tzinfo=None).isoformat(timespec="seconds") + "Z"


def _normalize_datetime_string(value: str) -> str:
    """Truncate or pad fractional seconds to exactly 6 digits for %f compatibility."""
    if "." not in value:
        return value
    before, _, after = value.partition(".")
    tz_marker = ""
    for marker in ("Z", "+", "-"):
        if marker in after:
            index = after.find(marker)
            tz_marker = after[index:]
            after = after[:index]
            break
    frac = after[:6].ljust(6, "0")
    return f"{before}.{frac}{tz_marker}"


def parse_datetime(value: Union[str, datetime, None]) -> Optional[datetime]:
    """
    Converts string representations of Edm.DateTime/Edm.DateTimeOffset to datetime.

    Args:
        value: Input value (string, datetime, or None)

    Returns:
        Parsed datetime or None if conversion fails

    Examples:
        >>> parse_datetime("2023-01-01T12:00:00Z")
        datetime.datetime(2023, 1, 1, 12, 0)
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value

    known_formats = [
        "%Y-%m-%dT%H:%M:%SZ",  # ISO 8601 UTC
        "%Y-%m-%dT%H:%M:%S.%fZ",  # ISO 8601 with microseconds
        "%Y-%m-%dT%H:%M:%S",  # Without timezone
        "%Y-%m-%dT%H:%M:%S.%f",  # With microseconds no TZ
        "%Y-%m-%dT%H:%M:%S%z",  # ISO 8601 with numeric offset
        "%Y-%m-%dT%H:%M:%S.%f%z",  # ISO 8601 with microseconds and offset
        "%Y-%m-%d",  # Date only
    ]

    if isinstance(value, str):
        value = _normalize_datetime_string(value)

    for fmt in known_formats:
        try:
            result = datetime.strptime(value, fmt)
            if result.tzinfo is None and fmt.endswith("Z"):
                result = result.replace(tzinfo=timezone.utc)
            return result
        except ValueError:
            continue
    return None
