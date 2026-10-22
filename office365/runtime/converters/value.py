"""Value-level conversion between stored values and their JSON representation.

The shared conversion layer: ``serialize_value`` maps stored values to their JSON
form (used by ``ClientObject``/``ClientValue``/``ClientValueCollection``
``to_json``), and ``coerce_value``/``declared_type`` map raw values to their
declared type (used by ``set_property``). Control information is not this
layer's business: a profile attaches it (``JsonProfile.wrap``).
"""

from __future__ import annotations

import re
import types
import uuid
from datetime import date, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple, Union, get_args, get_origin, get_type_hints

from office365.runtime.converters.scalars import parse_bool, parse_datetime, parse_enum, try_float, try_int
from office365.runtime.schema import EMPTY

if TYPE_CHECKING:
    from office365.runtime.odata.json_format import JsonProfile

_UNSET = object()
_NoneType = type(None)

_SCALAR_CONVERTERS = {
    bool: parse_bool,
    int: try_int,
    float: try_float,
    datetime: parse_datetime,
}

_declared_cache: Dict[Tuple[type, str], Any] = {}


def _serialize_enum(value: Enum, profile: Optional[JsonProfile]) -> Any:
    """Serialize an enum member for the active OData dialect.

    OData V3 (SharePoint) enums travel as their numeric value
    (``FieldTypeKind`` is ``Edm.Int32``); OData V4 / Graph enums travel as
    the member *name* ("teamsForBusiness") — the dialect says which. Enums
    generated with string values already match their name; older Graph ones
    (e.g. auto-numbered ``unknown = 0``) must fall back to the name, not the
    ordinal.

    A generated Graph enum carries the *CSDL ordinal* as a string
    (``TaskStatus.completed = "2"``), which is not a wire value — Graph
    rejects it, so a digit-only string falls back to the member name too.
    """
    if profile is not None and not profile.dialect.enum_by_name and isinstance(value.value, int):
        return value.value
    if isinstance(value.value, str):
        return value.name if value.value.isdigit() else value.value
    return value.name


def serialize_value(  # noqa: PLR0911 - one return per stored-value kind
    value: Any, profile: Optional[JsonProfile] = None
) -> Any:
    """Convert a stored value to its JSON representation.

    Handles ``ClientObject``/``ClientValue``/``ClientValueCollection`` (via their
    ``to_json``), ``Enum`` -> value, ``datetime``/``date`` -> ISO 8601, ``bytes``
    -> UTF-8, ``UUID`` -> str. A plain ``dict``/``list``/``tuple`` is descended into,
    so a container assembled by hand (a nested payload, a ``to_json`` result, a
    request body) is as JSON-safe as a generated value. Any other value (scalar,
    ``None``, ``ClientResult``) passes through unchanged.

    ``to_json`` is consulted *before* the container branches: a collection type may
    subclass ``dict``/``list`` and still need its own serialization.
    """
    if isinstance(value, Enum):
        return _serialize_enum(value, profile)
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, bytes):
        return value.decode("utf-8")
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if hasattr(value, "to_json"):
        return value.to_json(profile)
    if isinstance(value, dict):
        return {k: serialize_value(item, profile) for k, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serialize_value(item, profile) for item in value]
    return value


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
    meta = getattr(cls, "_schema", EMPTY).properties.get(name)
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
        except NameError:
            # A TYPE_CHECKING-only annotation: the getter constructs the type at
            # runtime, but the name is not resolvable here.
            declared = None
        except TypeError:
            # ``attr`` is not a function (a class constant sharing the wire name).
            declared = None
        if declared is not None:
            return _unwrap_type(declared)
    try:
        declared = get_type_hints(cls).get(name)
    except NameError:
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


def coerce_value(target_type: Any, value: Any, current: Any, persist_changes: bool) -> Any:
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
