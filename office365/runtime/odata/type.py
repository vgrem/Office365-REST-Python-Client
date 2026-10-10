from __future__ import annotations

import datetime
import uuid
from typing import Optional, Type

from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.types.collections import GuidCollection, StringCollection

#: OData primitive type names -> Python types (shared by the runtime and the
#: generator: serialization and code generation must agree on the grammar).
PRIMITIVE_PY_TYPES = {
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
    "Edm.Time": datetime.time,  # OData v3 name for a time-of-day (kept after TimeOfDay for reverse lookup)
    "Edm.Json": dict,
    "Collection(SP.KeyValue)": dict,
    "Collection(Edm.Guid)": GuidCollection,
    "Collection(Edm.String)": StringCollection,
    "Collection(Edm.Int32)": ClientValueCollection[int],
}


class ODataType:
    """Pure OData type-name utilities (no model resolution / code generation)."""

    @staticmethod
    def strip_collection(type_name: str | None) -> str | None:
        """Returns the item type of ``Collection(...)`` or the type itself."""
        if type_name is not None and type_name.startswith("Collection(") and type_name.endswith(")"):
            return type_name[len("Collection(") : -1]
        return type_name

    @staticmethod
    def is_collection_name(type_name: str | None) -> bool:
        """Whether the OData type name represents a collection."""
        return type_name is not None and type_name.startswith("Collection(") and type_name.endswith(")")

    @classmethod
    def item_type_name(cls, type_name: str | None) -> str | None:
        """Returns the collection item type name, or the type name itself."""
        return cls.strip_collection(type_name)

    @staticmethod
    def normalize_class_name(name: str) -> str:
        """Pascal-cases the last segment of an OData type reference."""
        return name[0].upper() + name[1:]

    @classmethod
    def normalize_type_name(cls, type_name: str | None) -> str | None:
        """Normalizes an OData type reference to the generated model key.

        Strips ``Collection(...)`` and Pascal-cases the last segment (e.g.
        ``microsoft.graph.user`` -> ``microsoft.graph.User``).
        """
        item_type = cls.strip_collection(type_name)
        if item_type is None:
            return None
        namespace, _, short_name = item_type.rpartition(".")
        if not namespace:
            return item_type
        return f"{namespace}.{cls.normalize_class_name(short_name)}"

    @classmethod
    def resolve_type_name(cls, client_type: Type) -> Optional[str]:
        """Resolves the OData type name for a given Python type.

        Args:
            client_type: The Python type to resolve (class or instance)

        Returns:
            The OData type name or None if unknown

        Examples:
            >>> ODataType.resolve_type_name(str)
            'Edm.String'
            >>> ODataType.resolve_type_name(ClientValue)
            'SP.ClientValue'
        """
        from office365.runtime.client_value import ClientValue

        try:
            if issubclass(client_type, ClientValue):
                return client_type().entity_type_name  # type: ignore[call-arg]
        except TypeError:
            pass

        for odata_type, py_type in PRIMITIVE_PY_TYPES.items():
            if py_type == client_type:
                return odata_type
        return None

    @staticmethod
    def primitive_type_for(type_name: str | None) -> Optional[Type]:
        """Returns the Python type for a known OData primitive, if any."""
        return PRIMITIVE_PY_TYPES.get(type_name) if type_name is not None else None

    @staticmethod
    def is_primitive_name(type_name: str | None) -> bool:
        """Whether the OData type name is a known primitive."""
        return type_name in PRIMITIVE_PY_TYPES
