"""Classify OData type references and render their Python annotations/defaults.

Covers operation return types (:class:`ReturnType`) and parameters
(:class:`ParameterType`), plus the :class:`TypeKind` shape enum. Resolution is
delegated to a :class:`~generator.builders.resolution.TypeRegistry` (only used to
tell client values from entities).
"""

from __future__ import annotations

import datetime
import uuid
from enum import Enum
from typing import TYPE_CHECKING, Optional

from office365.runtime.client_value import ClientValue

from generator.builders.naming import item_name, python_name
from generator.odata.type_system import (
    is_collection_name,
    is_primitive_name,
    primitive_type_for,
    strip_collection,
)

if TYPE_CHECKING:
    from generator.builders.resolution import TypeRegistry

_PRIMITIVE_DEFAULTS = {
    bool: "bool()",
    int: "int()",
    float: "float()",
    str: "str()",
    bytes: "bytes()",
    uuid.UUID: "UUID(int=0)",
    datetime.datetime: "datetime.min",
    datetime.date: "datetime.min",
    datetime.time: "time.min",
    datetime.timedelta: "datetime.timedelta(0)",
    dict: "{}",
}

_PYTHON_TYPE_NAMES = {
    str: "str",
    int: "int",
    float: "float",
    bool: "bool",
    bytes: "bytes",
    uuid.UUID: "UUID",
    datetime.datetime: "datetime",
    datetime.date: "date",
    datetime.time: "time",
}

_COLLECTION_WRAPPERS = {str: "StringCollection", uuid.UUID: "GuidCollection"}


class TypeKind(Enum):
    """Shape of an OData type reference."""

    VOID = "void"
    PRIMITIVE = "primitive"
    CLIENT_VALUE = "client_value"
    ENTITY = "entity"
    PRIMITIVE_COLLECTION = "primitive_collection"
    CLIENT_VALUE_COLLECTION = "client_value_collection"
    ENTITY_COLLECTION = "entity_collection"


class ReturnType:
    """Classifies a type name once and renders its annotation and default value."""

    def __init__(self, type_name: str | None, registry: Optional["TypeRegistry"] = None) -> None:
        self._name = type_name or ""
        self._registry = registry
        self.kind = self._classify()

    @property
    def is_void(self) -> bool:
        return self.kind is TypeKind.VOID

    @property
    def is_stream(self) -> bool:
        return self._name == "Edm.Stream"

    @property
    def annotation(self) -> str:
        """The Python type annotation (without ``ClientResult`` for voids)."""
        name = self._name
        if self.kind in (TypeKind.PRIMITIVE, TypeKind.CLIENT_VALUE):
            return f"ClientResult[{python_name(name)}]"
        if self.kind is TypeKind.ENTITY:
            return python_name(name)
        if self.kind is TypeKind.PRIMITIVE_COLLECTION:
            return f"ClientResult[{self._collection_name(name)}]"
        if self.kind is TypeKind.CLIENT_VALUE_COLLECTION:
            return f"ClientResult[ClientValueCollection[{item_name(name)}]]"
        return f"EntityCollection[{item_name(name)}]"

    def default(self, context: str) -> str:
        """The expression that constructs the return value for ``context``."""
        name = self._name
        if self.kind is TypeKind.PRIMITIVE:
            return f"ClientResult({context}, {_primitive_default(name)})"
        if self.kind is TypeKind.CLIENT_VALUE:
            return f"ClientResult({context}, {python_name(name)}())"
        if self.kind is TypeKind.ENTITY:
            return f"{python_name(name)}({context})"
        if self.kind is TypeKind.PRIMITIVE_COLLECTION:
            return f"ClientResult({context}, {self._collection_default(name)})"
        if self.kind is TypeKind.CLIENT_VALUE_COLLECTION:
            return f"ClientResult({context}, ClientValueCollection[{item_name(name)}]())"
        return f"EntityCollection({context}, {item_name(name)})"

    def _classify(self) -> TypeKind:
        name = self._name
        if not name:
            return TypeKind.VOID
        if is_collection_name(name):
            return self._classify_collection(name)
        if is_primitive_name(name):
            return TypeKind.PRIMITIVE
        if self._is_client_value(name):
            return TypeKind.CLIENT_VALUE
        return TypeKind.ENTITY

    def _classify_collection(self, name: str) -> TypeKind:
        item_type = strip_collection(name)
        if is_primitive_name(name) or is_primitive_name(item_type):
            return TypeKind.PRIMITIVE_COLLECTION
        if self._is_client_value(item_type):
            return TypeKind.CLIENT_VALUE_COLLECTION
        return TypeKind.ENTITY_COLLECTION

    def _is_client_value(self, type_name: str | None) -> bool:
        if self._registry is None:
            return False
        cls = self._registry.resolve(type_name)
        return cls is not None and issubclass(cls, ClientValue)

    @staticmethod
    def _collection_name(type_name: str) -> str:
        """Python annotation for a collection whose item type is primitive."""
        mapped = primitive_type_for(type_name) if is_primitive_name(type_name) else None
        if mapped is None:
            return python_name(type_name)
        item_types = getattr(mapped, "__args__", None)
        if item_types:
            return f"{mapped.__name__}[{item_types[0].__name__}]"
        return mapped.__name__

    @staticmethod
    def _collection_default(type_name: str) -> str:
        """Python default expression for a collection whose item type is primitive."""
        if is_primitive_name(type_name):
            mapped = primitive_type_for(type_name)
            assert mapped is not None
            item_types = getattr(mapped, "__args__", None)
            if item_types:
                return f"ClientValueCollection({item_types[0].__name__})"
            return f"{mapped.__name__}()"
        item_type = strip_collection(type_name)
        primitive = primitive_type_for(item_type)
        if primitive is not None:
            return f"ClientValueCollection({primitive.__name__})"
        return f"{python_name(type_name)}()"


def _primitive_default(type_name: str | None) -> str:
    """Default expression for a primitive OData type (``Edm.Int32`` -> ``int()``)."""
    return _PRIMITIVE_DEFAULTS.get(primitive_type_for(type_name), "None")


class ParameterType:
    """Python annotation and runtime wrapping for an operation parameter.

    Primitive collections are exposed as plain Python lists (``list[str]``,
    ``list[UUID]``) and wrapped into the matching runtime collection when the
    query payload is built.
    """

    def __init__(self, type_name: str | None) -> None:
        self._type_name = type_name
        self._item_type = strip_collection(type_name)
        self._python_item = self._resolve_python_item()

    def _resolve_python_item(self) -> Optional[type]:
        if self._type_name is None or not is_collection_name(self._type_name):
            return None
        if not is_primitive_name(self._item_type):
            return None
        return primitive_type_for(self._item_type)

    @property
    def is_primitive_collection(self) -> bool:
        return self._python_item in _PYTHON_TYPE_NAMES

    @property
    def annotation(self) -> str:
        if self.is_primitive_collection:
            return f"list[{_PYTHON_TYPE_NAMES[self._python_item]}]"
        return python_name(self._type_name)

    @property
    def wrapper(self) -> Optional[str]:
        """Runtime collection class used to wrap the argument, if any."""
        if not self.is_primitive_collection:
            return None
        return _COLLECTION_WRAPPERS.get(self._python_item, "ClientValueCollection")

    def wrap(self, expression: str) -> str:
        """Wrap a plain Python list argument into its runtime collection."""
        wrapper = self.wrapper
        if wrapper is None:
            return expression
        if wrapper == "ClientValueCollection":
            return f"ClientValueCollection({_PYTHON_TYPE_NAMES[self._python_item]}, {expression})"
        return f"{wrapper}({expression})"
