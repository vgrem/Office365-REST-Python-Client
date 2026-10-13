"""Helpers for building OData literals safely."""

from __future__ import annotations

from typing import Any


def escape_odata_string(value: str) -> str:
    """Escape a string for use inside an OData ``'...'`` literal.

    Both OData v3 (SharePoint) and v4 (Microsoft Graph) escape an embedded
    single quote by doubling it, so ``O'Brien`` becomes ``O''Brien`` when used
    in a filter such as ``displayName eq 'O''Brien'``.

    Args:
        value: The raw string value.

    Returns:
        The escaped value, safe to embed between single quotes.
    """
    return value.replace("'", "''")


def odata_literal(value: Any) -> str:
    """Format a Python value as an OData literal for a filter expression.

    Strings (and any other non-numeric value) are single-quoted and escaped;
    booleans and numbers are emitted bare, and ``None`` becomes ``null``. This
    is the missing half of :func:`escape_odata_string`, so a filter can be built
    from an arbitrary key/value without hand-rolling the quoting::

        >>> f"appId eq {odata_literal('0000-1111')}"
        "appId eq '0000-1111'"
        >>> f"Id eq {odata_literal(42)}"
        'Id eq 42'

    Args:
        value: The raw right-hand-side value of a comparison.

    Returns:
        The value formatted as an OData literal.
    """
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if value is None:
        return "null"
    return f"'{escape_odata_string(str(value))}'"
