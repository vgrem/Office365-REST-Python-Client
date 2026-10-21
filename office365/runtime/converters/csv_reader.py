"""CSV/records parsing for the collection import pipeline.

CSV files and JSON/Excel/pandas records are normalized into plain ``dict``
records (via :func:`coerce_records`) which the collection ``from_*`` methods
turn into entities via the shared conversion core (``create_typed_object`` ->
``set_property`` -> ``coerce_value``/``declared_type``).
"""

from __future__ import annotations

import csv
import warnings
from typing import IO, Any, get_origin

from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.converters.value import declared_type

_LIST_SEPARATOR = "; "


def read_csv_records(file: IO[str], delimiter: str = ",") -> list[dict]:
    """Parse CSV rows into plain dict records (empty cells dropped).

    Type-aware normalization (dotted keys, ``"; "`` collection splitting,
    unknown-column skipping) is applied later by :func:`coerce_records` when the
    records are imported.
    """
    reader = csv.DictReader(file, delimiter=delimiter)
    if reader.fieldnames is None:
        return []
    return [{k: v for k, v in row.items() if v not in ("", None)} for row in reader]


def coerce_records(item_type: type, records: list[dict], *, allow_unknown: bool = False) -> list[dict]:
    """Normalize plain dict records to the entity's declared property types.

    Dotted keys (``a/b/c``) are re-nested into dicts; ``"; "``-joined strings are
    split for collection-typed fields; non-importable keys (``@*``, ``id``) and
    ``None`` cells are dropped; columns mapping to no known property are skipped
    with a warning. Pass ``allow_unknown=True`` for schema-flexible targets whose
    fields are only known at runtime (SharePoint list items). Shared by every
    import format.
    """
    coerced: list[dict[str, Any]] = []
    for record in records:
        item: dict[str, Any] = {}
        for key, raw in record.items():
            if not _is_importable(key):
                continue
            if raw is None:
                continue
            if "/" in key:
                nav = key.split("/", 1)[0]
                if declared_type(item_type, nav) is None and not allow_unknown:
                    warnings.warn(f"Skipping unknown column '{key}'", stacklevel=2)
                    continue
                _set_nested(item, key, raw)
                continue
            declared = declared_type(item_type, key)
            if declared is None and not allow_unknown:
                warnings.warn(f"Skipping unknown column '{key}'", stacklevel=2)
                continue
            if isinstance(raw, str) and declared is not None and _is_collection(declared):
                item[key] = raw.split(_LIST_SEPARATOR)
            else:
                item[key] = raw
        coerced.append(item)
    return coerced


def clean_records(records: list[dict]) -> list[dict]:
    """Strip non-importable cells (``@*``, ``id``, ``None``) from JSON records."""
    return [{k: v for k, v in record.items() if _is_importable(k) and v is not None} for record in records]


def _is_importable(key: str) -> bool:
    """Decide whether a record key should be imported at all."""
    return not key.startswith("@") and key != "id"


def _is_collection(target_type: Any) -> bool:
    """Decide whether a declared type represents a list/collection field."""
    return get_origin(target_type) in (list, tuple, set) or (
        isinstance(target_type, type) and issubclass(target_type, ClientValueCollection)
    )


def _set_nested(record: dict[str, Any], key: str, value: Any) -> None:
    """Re-nest a dotted header (``a/b/c``) into nested dicts."""
    parts = key.split("/")
    node = record
    for part in parts[:-1]:
        node = node.setdefault(part, {})
    node[parts[-1]] = value
