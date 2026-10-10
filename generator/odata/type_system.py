"""The generator's OData type grammar.

OData type references are strings (``Collection(microsoft.graph.User)``); this
module parses them once into a :class:`TypeRef` value object and provides the
normalization the code generator needs (Pascal-cased model keys). The
``Edm.*`` primitive <-> Python mapping is shared with the runtime, so
serialization and code generation cannot disagree.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Type

from office365.runtime.odata.type import PRIMITIVE_PY_TYPES, ODataType

_COLLECTION_PREFIX = "Collection("


def is_collection_name(type_name: Optional[str]) -> bool:
    """Whether the OData type name is a ``Collection(...)``."""
    return ODataType.is_collection_name(type_name)


def strip_collection(type_name: Optional[str]) -> Optional[str]:
    """The element type of ``Collection(...)``, or the name unchanged."""
    return ODataType.strip_collection(type_name)


def item_type_name(type_name: Optional[str]) -> Optional[str]:
    """The element type of ``Collection(...)``, or the name itself."""
    return strip_collection(type_name)


def is_primitive_name(type_name: Optional[str]) -> bool:
    """Whether the OData type name is a known primitive (incl. primitive collections)."""
    return type_name in PRIMITIVE_PY_TYPES


def primitive_type_for(type_name: Optional[str]) -> Optional[Type]:
    """The Python type for a known OData primitive, if any."""
    return ODataType.primitive_type_for(type_name)


def normalize_class_name(name: str) -> str:
    """Pascal-case the last segment of an OData type reference."""
    return name[0].upper() + name[1:] if name else name


def normalize_type_name(type_name: Optional[str]) -> Optional[str]:
    """Normalize an OData reference to the generated model key.

    ``Collection(...)`` is stripped and the last segment Pascal-cased, e.g.
    ``microsoft.graph.user`` -> ``microsoft.graph.User``.
    """
    item_type = strip_collection(type_name)
    if item_type is None:
        return None
    namespace, _, short_name = item_type.rpartition(".")
    if not namespace:
        return item_type
    return f"{namespace}.{normalize_class_name(short_name)}"


@dataclass(frozen=True)
class TypeRef:
    """A parsed OData type reference (immutable; parse once, read many)."""

    raw: Optional[str] = None

    @classmethod
    def of(cls, raw: Optional[str]) -> "TypeRef":
        """Wrap a raw OData type reference (``None`` is allowed)."""
        return cls(raw)

    @property
    def is_collection(self) -> bool:
        return is_collection_name(self.raw)

    @property
    def element(self) -> "TypeRef":
        """The element type (``self`` when this is not a collection)."""
        return TypeRef(strip_collection(self.raw))

    @property
    def text(self) -> Optional[str]:
        """The element type name as text (``Collection(...)`` stripped)."""
        return self.element.raw

    @property
    def normalized(self) -> Optional[str]:
        """The generated model key (element, Pascal-cased)."""
        return normalize_type_name(self.raw)

    @property
    def namespace(self) -> str:
        """The namespace of the element type."""
        return (self.text or "").rpartition(".")[0]

    @property
    def short_name(self) -> str:
        """The (Pascal-cased) short name of the element type."""
        return normalize_class_name((self.text or "").rpartition(".")[2])

    @property
    def is_primitive(self) -> bool:
        return is_primitive_name(self.raw)

    @property
    def python_type(self) -> Optional[Type]:
        """The Python type for a primitive reference, if any."""
        return primitive_type_for(self.raw)
