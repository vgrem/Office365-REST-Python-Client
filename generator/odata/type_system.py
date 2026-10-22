"""The generator's OData type grammar.

OData spells a type reference as text — ``Edm.String``, ``microsoft.graph.User``,
``Collection(microsoft.graph.User)``. Reading that text is CSDL work and belongs to
the generator; the runtime asks the inverse question ("what is *this* Python class's
EDM name?") through :mod:`office365.runtime.odata.edm`.

There is exactly one reader (:meth:`TypeRef.parse`) and one place that spells a
wrapper back out (:attr:`TypeRef.text`). Everything else is a question asked of the
parsed value, so "is this a collection?" is a fact fixed when the reference is read
rather than a string test repeated at every call site.
"""

from __future__ import annotations

from typing import Any, Optional

from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.odata.edm import PRIMITIVE_PY_TYPES
from office365.runtime.odata.edm import primitive_type_for as _primitive_for
from office365.runtime.types.collections import GuidCollection, StringCollection

__all__ = [
    "PRIMITIVE_PY_TYPES",
    "TypeRef",
    "normalize_class_name",
]

#: The wrapper marker; ``_WRAPPER + "("`` opens a collection reference and
#: :attr:`TypeRef.text` closes it again, so the two spellings cannot drift apart.
_WRAPPER = "Collection"

#: How a primitive collection is generated. A code-generation choice (``list[str]``
#: vs ``StringCollection``), not grammar, so it lives here rather than in the shared
#: EDM table — and the runtime no longer imports these classes to parse a name.
_COLLECTION_PY_TYPES: dict[str, Any] = {
    "Edm.String": StringCollection,
    "Edm.Guid": GuidCollection,
    "Edm.Int32": ClientValueCollection[int],
    "SP.KeyValue": dict,
}


def normalize_class_name(name: str) -> str:
    """Pascal-case the last segment of an OData type name (a case rule, not a grammar)."""
    return name[0].upper() + name[1:] if name else name


class TypeRef:
    """A type reference read once: the element's name, plus whether it is a collection.

    ``TypeRef.parse("Collection(microsoft.graph.user)")`` is a collection of
    ``microsoft.graph.user``; the wrapper never has to be stripped again.
    """

    __slots__ = ("name", "is_collection")

    def __init__(self, name: Optional[str] = None, is_collection: bool = False) -> None:
        self.name = name
        self.is_collection = is_collection

    @classmethod
    def parse(cls, raw: Optional[str]) -> "TypeRef":
        """Read a reference string (``None`` is allowed and reads as "no type")."""
        opening = _WRAPPER + "("
        if raw is not None and raw.startswith(opening) and raw.endswith(")"):
            name = raw[len(opening) : -1]
            if name:
                return cls(name, is_collection=True)
        return cls(raw)

    @property
    def text(self) -> Optional[str]:
        """The reference spelled the way OData spells it, wrapper included."""
        return f"{_WRAPPER}({self.name})" if self.is_collection else self.name

    @property
    def element(self) -> "TypeRef":
        """The element type (``self`` when this is not a collection)."""
        return TypeRef(self.name) if self.is_collection else self

    @property
    def normalized(self) -> Optional[str]:
        """The generated model key (element, last segment Pascal-cased)."""
        if self.name is None:
            return None
        namespace, _, short_name = self.name.rpartition(".")
        if not namespace:
            return self.name
        return f"{namespace}.{normalize_class_name(short_name)}"

    @property
    def namespace(self) -> str:
        """The namespace of the element type."""
        return (self.name or "").rpartition(".")[0]

    @property
    def short_name(self) -> str:
        """The (Pascal-cased) short name of the element type."""
        return normalize_class_name((self.name or "").rpartition(".")[2])

    @property
    def is_primitive(self) -> bool:
        """Whether the element is an ``Edm.*`` primitive this project can map."""
        if self.is_collection:
            return self.name in PRIMITIVE_PY_TYPES or self.name in _COLLECTION_PY_TYPES
        return self.name in PRIMITIVE_PY_TYPES

    @property
    def python_type(self) -> Optional[Any]:
        """The Python type for a primitive reference, if any."""
        if self.is_collection:
            return _COLLECTION_PY_TYPES.get(self.name or "")
        return _primitive_for(self.name)

    def __repr__(self) -> str:
        return f"TypeRef({self.text!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TypeRef):
            return NotImplemented
        return (self.name, self.is_collection) == (other.name, other.is_collection)

    def __hash__(self) -> int:
        return hash((self.name, self.is_collection))
