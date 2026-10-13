"""Human-readable rendering for runtime objects and values.

This module powers ``repr()``/``str()`` for :class:`~office365.runtime.client_object.ClientObject`
and :class:`~office365.runtime.client_value.ClientValue`. The rendering is intentionally:

* **local** - it projects only what is already loaded, never triggering a network call;
* **bounded** - long strings, primitive sequences and the number of fields are truncated;
* **recursion-safe** - nested client objects/values are rendered at most one level deep.

The limits are module level so they can be tuned globally (mirroring numpy/pandas
display options) without touching the classes themselves.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from itertools import islice
from typing import Any, Iterator, Sequence, Tuple

#: Maximum number of top-level fields rendered for a single object.
MAX_FIELDS = 6
#: Maximum length of a single rendered value (longer values are elided).
MAX_STRING = 60
#: Maximum number of items rendered from a primitive sequence.
MAX_ITEMS = 5
#: Maximum nesting depth for client objects/values embedded in another object.
MAX_DEPTH = 1
#: Maximum number of columns rendered for a collection preview.
MAX_COLUMNS = 6
#: Maximum width of a single table column (wide enough for a full GUID).
MAX_COLUMN_WIDTH = 36
#: Indentation applied to collection preview rows.
_INDENT = "  "


def _shorten(text: str) -> str:
    """Truncate ``text`` to :data:`MAX_STRING`, marking the elision with ``…``."""
    if len(text) <= MAX_STRING:
        return text
    return text[: MAX_STRING - 1] + "…"


def _is_unset(value: Any) -> bool:
    """Whether a property/field should be omitted from a rendering."""
    if value is None:
        return True
    # ``datetime.min`` is the sentinel used for absent date properties.
    return isinstance(value, datetime) and value == datetime.min


def _format_scalar(value: Any) -> str:
    """Render a primitive/leaf value."""
    if isinstance(value, str):
        return _shorten(value)
    if isinstance(value, bool):
        return "True" if value else "False"
    if isinstance(value, Enum):
        return str(value.name)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return _shorten(str(value))


def format_value(value: Any, depth: int = 0, max_items: int = MAX_ITEMS) -> str:
    """Render a single property/field value, bounded and recursion-safe."""
    from office365.runtime.client_object import ClientObject
    from office365.runtime.client_value import ClientValue
    from office365.runtime.client_value_collection import ClientValueCollection

    if isinstance(value, (ClientValueCollection, list, tuple)):
        preview = list(islice(value, max_items))
        rendered = ", ".join(format_value(item, depth) for item in preview)
        if len(value) > max_items:
            rendered = f"{rendered}, …" if rendered else "…"
        return f"[{rendered}]"
    if isinstance(value, dict):
        rendered = ", ".join(f"{k}: {format_value(v, depth)}" for k, v in list(value.items())[:max_items])
        return f"{{{rendered}}}"
    if isinstance(value, (ClientObject, ClientValue)):
        if depth >= MAX_DEPTH:
            return f"{type(value).__name__}(…)"
        return describe(value, depth + 1)
    return _format_scalar(value)


def _fields(obj: Any) -> Iterator[Tuple[str, Any]]:
    """Iterate ``(name, value)`` pairs for a client object or value."""
    from office365.runtime.client_object import ClientObject

    if isinstance(obj, ClientObject):
        return iter(obj.properties.items())
    return iter(vars(obj).items())


def describe(obj: Any, depth: int = 0) -> str:
    """Return a compact ``ClassName(field=value, …)`` rendering of ``obj``."""
    fields = [(name, value) for name, value in _fields(obj) if not _is_unset(value)]
    rendered = [f"{name}={format_value(value, depth)}" for name, value in fields[:MAX_FIELDS]]
    body = ", ".join(rendered)
    if len(fields) > MAX_FIELDS:
        body = f"{body}, …" if body else "…"
    return f"{type(obj).__name__}({body})"


def _record_fields(item: Any) -> dict[str, Any] | None:
    """Return the displayable fields of a collection item, or ``None`` for scalars."""
    from office365.runtime.client_object import ClientObject
    from office365.runtime.client_value import ClientValue
    from office365.runtime.client_value_collection import ClientValueCollection

    if isinstance(item, ClientValueCollection):
        return None
    if isinstance(item, ClientObject):
        return {k: v for k, v in item.properties.items() if not k.startswith("_") and not _is_unset(v)}
    if isinstance(item, ClientValue):
        return {k: v for k, v in vars(item).items() if not k.startswith("_") and not _is_unset(v)}
    return None


def _columns_and_rows(items: Sequence[Any]) -> tuple[list[str] | None, list[dict[str, Any]] | None]:
    """Build the column set (first-seen union) and per-item field maps."""
    records: list[dict[str, Any]] = []
    for item in items:
        fields = _record_fields(item)
        if fields is None:
            return None, None
        records.append(fields)
    columns: list[str] = []
    for record in records:
        for name in record:
            if name not in columns:
                columns.append(name)
    return columns[:MAX_COLUMNS], records


def _cell(value: Any) -> str:
    """Render a single table cell value onto one line."""
    return format_value(value).replace("\n", " ")


def _render_table(
    columns: list[str], records: list[dict[str, Any]], max_column_width: int | None = MAX_COLUMN_WIDTH
) -> str:
    """Render an aligned table; columns are width-bounded unless ``max_column_width`` is ``None``."""
    rows = [[_cell(record.get(column, "")) for column in columns] for record in records]
    widths = []
    for index, column in enumerate(columns):
        width = max([len(column), *(len(row[index]) for row in rows)])
        widths.append(width if max_column_width is None else min(width, max_column_width))
    lines = [_INDENT + "  ".join(column[: widths[i]].ljust(widths[i]) for i, column in enumerate(columns)).rstrip()]
    for row in rows:
        lines.append(_INDENT + "  ".join(row[i][: widths[i]].ljust(widths[i]) for i in range(len(columns))).rstrip())
    return "\n".join(lines)


def describe_collection(
    items: Any,
    name: str,
    *,
    max_items: int | None = MAX_ITEMS,
    max_column_width: int | None = MAX_COLUMN_WIDTH,
    more: bool = False,
) -> str:
    """Return a bounded, pandas-like preview of an already-loaded collection.

    Only the items handed in are inspected — nothing is fetched, so calling
    ``repr()``/``str()`` on a collection is always safe and cheap. Record-like
    items (client objects/values) render as an aligned table; primitive items
    render as a concise list. Pass ``max_items=None`` to render every item and
    ``max_column_width=None`` to disable per-column truncation (both used by
    ``to_string()`` for full reports).

    Args:
        more: Whether the server may hold further, not-yet-loaded pages. When
            true the count is marked with ``+`` and a hint to call
            ``get_all()`` is appended, so a preview never implies the
            collection is complete.
    """
    footer = f"{_INDENT}(more pages available — call get_all() to load them)" if more else ""
    total = len(items)
    if total == 0:
        return "\n".join(part for part in (f"{name}([])", footer) if part)
    limit = total if max_items is None else max_items
    preview = list(islice(items, limit))
    columns, records = _columns_and_rows(preview)
    if columns is None or records is None or not columns:
        return "\n".join(part for part in (f"{name}({format_value(items, max_items=limit)})", footer) if part)
    lines = [
        f"{name}(count={total}{'+' if more else ''})",
        _render_table(columns, records, max_column_width),
    ]
    if len(preview) < total:
        lines.append(f"{_INDENT}… (+{total - len(preview)} more)")
    if footer:
        lines.append(footer)
    return "\n".join(lines)


def collection_html(items: Any, name: str, *, more: bool = False) -> str:
    """Render an already-loaded collection as an HTML table for Jupyter.

    Args:
        more: Whether the server may hold further pages (see
            :func:`describe_collection`); reflected in the count and a note.
    """
    import html

    total = len(items)
    suffix = "+" if more else ""
    note = " <i>(more pages available — call get_all())</i>" if more else ""
    if total == 0:
        return f"<div><b>{html.escape(name)}</b> (empty){note}</div>"
    preview = list(islice(items, MAX_ITEMS))
    columns, records = _columns_and_rows(preview)
    truncated = f" … (+{total - MAX_ITEMS} more)" if total > MAX_ITEMS else ""
    if columns is None or records is None or not columns:
        cells = "".join(f"<td>{html.escape(_cell(item))}</td>" for item in preview)
        return (
            f"<div><b>{html.escape(name)}</b> (count={total}{suffix}){truncated}{note}"
            f"<table><tr>{cells}</tr></table></div>"
        )
    head = "".join(f"<th>{html.escape(column)}</th>" for column in columns)
    body = "".join(
        "<tr>" + "".join(f"<td>{html.escape(_cell(record.get(column, '')))}</td>" for column in columns) + "</tr>"
        for record in records
    )
    return (
        f"<div><b>{html.escape(name)}</b> (count={total}{suffix}){truncated}{note}"
        f"<table border='1' cellspacing='0' cellpadding='3'>"
        f"<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"
    )
