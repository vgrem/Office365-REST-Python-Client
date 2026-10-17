"""Value-level conversion between stored values and their JSON representation.

The shared conversion layer: ``serialize_value`` maps stored values to their JSON
form (used by ``ClientObject``/``ClientValue``/``ClientValueCollection``
``to_json``), and ``deserialize_value``/``declared_type`` map raw values to their
declared type (used by ``set_property``). ``_add_type_metadata`` attaches the
OData type marker.
"""

from __future__ import annotations

import re
import types
import uuid
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, Optional, Tuple, Union, get_args, get_origin, get_type_hints

from office365.runtime.converters.scalars import parse_bool, parse_datetime, parse_enum, try_float, try_int
from office365.runtime.odata.json_format import ODataJsonFormat
from office365.runtime.odata.v3.json_light_format import JsonLightFormat

_UNSET = object()
_NoneType = type(None)

_SCALAR_CONVERTERS = {
    bool: parse_bool,
    int: try_int,
    float: try_float,
    datetime: parse_datetime,
}

_declared_cache: Dict[Tuple[type, str], Any] = {}


def _serialize_enum(value: Enum, json_format: Optional[ODataJsonFormat]) -> Any:
    """Serialize an enum member for the active OData dialect.

    OData V3 (SharePoint) enums travel as their numeric value
    (``FieldTypeKind`` is ``Edm.Int32``); OData V4 / Graph enums travel as
    the member *name* ("teamsForBusiness"). Enums generated with string
    values already match their name; older Graph ones (e.g. auto-numbered
    ``unknown = 0``) must fall back to the name, not the ordinal.

    A generated Graph enum carries the *CSDL ordinal* as a string
    (``TaskStatus.completed = "2"``), which is not a wire value — Graph
    rejects it, so a digit-only string falls back to the member name too.
    """
    if isinstance(json_format, JsonLightFormat) and isinstance(value.value, int):
        return value.value
    if isinstance(value.value, str):
        return value.name if value.value.isdigit() else value.value
    return value.name


def serialize_value(value: Any, json_format: Optional[ODataJsonFormat] = None) -> Any:
    """Convert a stored value to its JSON representation.

    Handles ``ClientObject``/``ClientValue``/``ClientValueCollection`` (via their
    ``to_json``), ``Enum`` -> value, ``datetime``/``date`` -> ISO 8601, ``bytes``
    -> UTF-8, ``UUID`` -> str. Any other value (scalar, ``None``, ``dict``,
    ``list``, ``ClientResult``) passes through unchanged.
    """
    if isinstance(value, Enum):
        return _serialize_enum(value, json_format)
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, bytes):
        return value.decode("utf-8")
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if hasattr(value, "to_json"):
        return value.to_json(json_format)
    return value


def _add_type_metadata(
    result: Dict[str, Any], json_format: Optional[ODataJsonFormat], entity_type_name: Optional[str]
) -> None:
    """Attach the OData type metadata marker when the format requests it."""
    if json_format is not None and json_format.include_control_information and entity_type_name is not None:
        if isinstance(json_format, JsonLightFormat):
            result[json_format.metadata_type] = {"type": entity_type_name}
        else:
            result[json_format.metadata_type] = "#" + entity_type_name


def to_snake_case(name: str) -> str:
    """Convert a camelCase property name to its snake_case Python attribute."""
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def _unwrap_type(target: Any) -> Any:
    """Strip Optional/Union wrappers from a type annotation."""
    origin = get_origin(target)
    if origin in (Union, getattr(types, "UnionType", None)):
        args = [a for a in get_args(target) if a is not _NoneType]
        return args[0] if len(args) == 1 else target
    return target


def declared_type(cls: type, name: str) -> Any:
    """Resolve the declared (unwrapped) type of a property/field by its OData name.

    Entities resolve the ``@odata``-mapped or snake_case getter's return
    annotation; ``ClientValue`` dataclasses the field annotation. ``None`` when
    unresolvable. Cached per ``(cls, name)``.
    """
    key = (cls, name)
    if key in _declared_cache:
        return _declared_cache[key]
    declared = _resolve_declared_type(cls, name)
    _declared_cache[key] = declared
    return declared


def _resolve_declared_type(cls: type, name: str) -> Any:
    meta = getattr(cls, "_odata_meta", {}).get(name)
    if meta is not None:
        attrs = (meta.attr,)
    else:
        # Generated getters rename reserved words with a trailing underscore
        # (``type`` -> ``type_``), a rename ``to_snake_case`` cannot express.
        attrs = (to_snake_case(name), to_snake_case(name) + "_")
    for attr in attrs:
        member = getattr(cls, attr, None)
        if member is None:
            continue
        target = member.fget if isinstance(member, property) else member
        try:
            declared = get_type_hints(target).get("return")
        except Exception:
            declared = None
        if declared is not None:
            return _unwrap_type(declared)
    try:
        declared = get_type_hints(cls).get(name)
    except Exception:
        declared = None
    return _unwrap_type(declared) if declared is not None else None


def is_client_value_type(target: Any) -> bool:
    """Whether a type annotation represents a ``ClientValue`` (or generic ``ClientValueCollection``).

    Uses the ``_is_client_value`` class marker so the conversion layer doesn't
    import ``ClientValue`` (avoiding a cycle). ``get_type_hints`` returns
    parametrized collections as a ``_GenericAlias``, so the origin is checked too.
    """
    cls = target if isinstance(target, type) else get_origin(target)
    return isinstance(cls, type) and getattr(cls, "_is_client_value", False)


def _client_value_origin(target: Any) -> type:
    """Return the concrete class of a ClientValue type annotation."""
    return target if isinstance(target, type) else get_origin(target)


def deserialize_declared(value: Any, declared_type: Any) -> Any:
    """Coerce a value to a declared scalar or enum type.

    Returns ``_UNSET`` when the declared type isn't a supported scalar/enum, so
    callers can fall back to their own handling.
    """
    converter = _SCALAR_CONVERTERS.get(declared_type)
    if converter is not None:
        return converter(value)
    if isinstance(declared_type, type) and issubclass(declared_type, Enum):
        return parse_enum(declared_type, value)
    return _UNSET


def deserialize_nested(base: Any, value: Any, persist_changes: bool) -> Any:
    """Apply a raw list/dict onto a nested ``ClientValue``/``ClientObject``
    (whose ``set_property`` maps list items by index and dict items by key),
    returning the stored value. Scalar values are returned as-is.
    """
    if isinstance(value, list):
        for i, p_v in enumerate(value):
            base.set_property(i, p_v, persist_changes)
    elif isinstance(value, dict):
        for k, p_v in value.items():
            base.set_property(k, p_v, persist_changes)
    else:
        return value
    return base


def deserialize_value(target_type: Any, value: Any, current: Any, persist_changes: bool) -> Any:
    """Coerce a raw value for storage by its declared type, falling back to the current instance.

    Declared scalars/enums go through ``deserialize_declared``; declared
    ``ClientValue``/``ClientValueCollection`` (including generic aliases) are
    populated via ``deserialize_nested``. Otherwise the value is coerced against
    the current instance (a nested ``ClientObject``/``ClientValue``, ``datetime``,
    ``Enum``) or passed through raw.
    """
    if target_type is not None and value is not None:
        coerced = deserialize_declared(value, target_type)
        if coerced is not _UNSET:
            return coerced
        if is_client_value_type(target_type):
            origin = _client_value_origin(target_type)
            if not isinstance(current, origin):
                current = origin()
            return deserialize_nested(current, value, persist_changes)
    if hasattr(current, "set_property") and not isinstance(current, (datetime, Enum)):
        return deserialize_nested(current, value, persist_changes)
    if isinstance(current, datetime):
        return parse_datetime(value)
    if isinstance(current, Enum):
        return current if value is None else parse_enum(type(current), value)
    return value
