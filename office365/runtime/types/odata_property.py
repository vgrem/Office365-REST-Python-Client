from __future__ import annotations

from dataclasses import dataclass

_ODATA_MARKER = "__odata__"


@dataclass
class ODataPropertyMeta:
    """Metadata for an ``@odata``-declared property.

    ``name`` is the JSON/OData key; ``attr`` is the Python attribute name,
    filled in by ``ClientObject.__init_subclass__`` at class creation.
    """

    name: str
    attr: str = ""
    persist: bool = False
    navigation: bool = False
    filterable: bool = False
    nullable: bool = True
    sortable: bool = False
    searchable: bool = False
    description: str = ""


def odata(name: str, **attrs: bool | str):
    """Declare OData metadata for a property.

    Args:
        name: The JSON key name in the Graph API response.
        **attrs: Optional attributes (persist, navigation, nullable, ...).

    ``navigation=True`` marks a CSDL ``NavigationProperty``: it is reached with
    ``$expand`` and cannot appear in ``$select``.
    """

    def decorator(method):
        meta = ODataPropertyMeta(name=name, **attrs)  # type: ignore[arg-type]
        target = method.fget if isinstance(method, property) else method
        setattr(target, _ODATA_MARKER, meta)
        return method

    return decorator
