from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from typing import Dict, TypeVar

_ODATA_MARKER = "__odata__"
_T = TypeVar("_T")

_FIELD_DECLARATIONS: Dict[type, Dict[str, "ODataPropertyMeta"]] = {}


@dataclass
class ODataPropertyMeta:
    """Metadata for an ``@odata``-declared property.

    ``name`` is the JSON/OData key; ``attr`` is the Python attribute name,
    filled in by ``ClientObject.__init_subclass__`` at class creation.
    """

    name: str
    attr: str = ""
    persist: bool = False
    readonly: bool = False
    navigation: bool = False
    filterable: bool = False
    nullable: bool = True
    sortable: bool = False
    searchable: bool = False
    description: str = ""


class odata(dict):
    """Declare the OData metadata of one property.

    A ``ClientObject`` has a property to decorate, so the declaration is applied to
    it::

        @odata(name="start")
        def start(self): ...

    A ``ClientValue`` is a dataclass: its fields are annotations, not properties, so
    the same declaration rides along in the field's metadata instead::

        start: DateTimeTimeZone | None = field(default=None, metadata=odata(name="start"))

    One name, one ``ODataPropertyMeta``, two carriers, because a field and a property
    are both a name plus an annotation. Being a ``Mapping`` is what makes the second
    form possible; being callable is what keeps the first one byte-identical.

    ``readonly=True`` marks a value the service assigns -- its id, its audit stamps,
    the organizer it resolved, the response it recorded: a response carries it, a
    request must not. ``navigation=True`` marks a CSDL ``NavigationProperty``: it is
    reached with ``$expand`` and cannot appear in ``$select``.
    """

    meta: ODataPropertyMeta

    def __init__(self, name: str, **attrs: bool | str) -> None:
        self.meta = ODataPropertyMeta(name=name, **attrs)  # type: ignore[arg-type]
        super().__init__({_ODATA_MARKER: self.meta})

    def __call__(self, method: _T) -> _T:
        target = method.fget if isinstance(method, property) else method  # type: ignore[attr-defined]
        setattr(target, _ODATA_MARKER, self.meta)
        return method


def field_declarations(cls: type) -> Dict[str, ODataPropertyMeta]:
    """The declared fields of a dataclass, by attribute name.

    Empty for anything that declares nothing -- a plain dataclass, a hand-written
    value, a ``ClientObject``. Declaring is opt-in, so the 2,887 nested types keep
    their attribute names until one of them has a fact to state.
    """
    cached = _FIELD_DECLARATIONS.get(cls)
    if cached is None:
        cached = (
            {f.name: f.metadata[_ODATA_MARKER] for f in fields(cls) if _ODATA_MARKER in f.metadata}
            if is_dataclass(cls)
            else {}
        )
        _FIELD_DECLARATIONS[cls] = cached
    return cached
