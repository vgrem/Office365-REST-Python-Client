"""The EDM grammar: primitive names, and the name a Python class declares.

OData type *references* are strings (``Collection(microsoft.graph.User)``) and are
CSDL syntax: only the generator parses them, once, into
:class:`generator.odata.type_system.TypeRef`. The runtime asks the inverse question —
"given this Python class, what does OData call it?" — which is a declaration read,
not string surgery::

    edm_type_name(str)  # "Edm.String"
    edm_type_name(Event)  # "microsoft.graph.Event"
    collection_type_name(Event)  # "Collection(microsoft.graph.Event)"

A generated model declares its name once, as a class fact (``_odata_type_name``), so
resolving a name never builds the model: a ``ClientObject`` subclass cannot be
constructed without a context, and a lookup that *needs* one is a lookup with a
hidden side effect. Classes generated before that fact existed fall back to reading
the name off one throwaway instance (cached per class).
"""

from __future__ import annotations

import datetime
import uuid
from functools import cache
from typing import Any, Optional, Type

#: OData primitive type names -> Python types. Several names share a Python type
#: (``Edm.Int32``/``Edm.Int64`` -> ``int``); the reverse lookup keeps the first row,
#: so ``int`` -> ``Edm.Int32`` and ``datetime.time`` -> ``Edm.TimeOfDay`` (the v4
#: spelling; ``Edm.Time`` is its v3 alias).
PRIMITIVE_PY_TYPES: dict[str, Any] = {
    "Edm.Boolean": bool,
    "Edm.Int32": int,
    "Edm.Int64": int,
    "Edm.Int16": int,
    "Edm.Byte": int,
    "Edm.SByte": int,
    "Edm.String": str,
    "Edm.Guid": uuid.UUID,
    "Edm.Single": float,
    "Edm.Double": float,
    "Edm.Decimal": float,
    "Edm.Binary": bytes,
    "Edm.Stream": bytes,
    "Edm.DateTimeOffset": datetime.datetime,
    "Edm.DateTime": datetime.datetime,
    "Edm.Duration": datetime.timedelta,
    "Edm.Date": datetime.date,
    "Edm.TimeOfDay": datetime.time,
    "Edm.Time": datetime.time,
    "Edm.Json": dict,
}

#: Python type -> the name the runtime writes for it (first row wins).
PY_PRIMITIVE_NAMES: dict[type, str] = {}
for _edm_name, _py_type in PRIMITIVE_PY_TYPES.items():
    PY_PRIMITIVE_NAMES.setdefault(_py_type, _edm_name)


def primitive_type_for(type_name: Optional[str]) -> Optional[Type]:
    """The Python type for a known OData primitive, if any."""
    if type_name is None:
        return None
    return PRIMITIVE_PY_TYPES.get(type_name)


@cache
def edm_type_name(client_type: type) -> Optional[str]:
    """The EDM name a Python class declares, or ``None`` when it declares none.

    The argument is the *class*, not an instance: a lookup must not build the thing
    it asks about, and an entity without a context cannot be built at all. It is
    annotated ``type`` rather than a union of the model base classes because
    primitives are first-class here (``ClientValueCollection(str)`` asks for
    ``"Collection(Edm.String)"``) and every generated model is produced by the code
    generator at build time — the runtime has no closed set of model classes to
    enumerate. What a declaration *is* is a protocol, documented below, not a
    hierarchy: the name is read from a class attribute, so nothing has to be
    imported to be asked.

    ``None`` is a real answer, not a failure: a type nothing named has no name to
    declare, and a marker naming a type nobody declared is worse than no marker.

    Resolution order: a primitive row in :data:`PRIMITIVE_PY_TYPES`, then the
    ``_odata_type_name`` class fact generated into every model, then a plain
    ``entity_type_name`` string attribute (a hand-written declaration), and only
    then one cached instance — the last resort for models that predate the fact.

    Args:
        client_type: a primitive Python type (``str``) or a model class.

    Returns:
        ``"Edm.String"`` for ``str``, ``"microsoft.graph.Event"`` for ``Event``.
    """
    primitive = PY_PRIMITIVE_NAMES.get(client_type)
    if primitive is not None:
        return primitive
    declared = getattr(client_type, "_odata_type_name", None)
    if declared is not None:
        return declared
    # A class may still declare the name as a plain attribute (older generated
    # values, duck-typed stubs) instead of the ``_odata_type_name`` fact.
    attribute = getattr(client_type, "entity_type_name", None)
    if isinstance(attribute, str):
        return attribute
    try:
        value = client_type()
    except TypeError:
        return None
    return getattr(value, "entity_type_name", None)


def collection_type_name(client_type: type) -> Optional[str]:
    """The ``Collection(...)`` name of an element class, or ``None`` when it declares none."""
    name = edm_type_name(client_type)
    if name is None:
        return None
    return f"Collection({name})"
