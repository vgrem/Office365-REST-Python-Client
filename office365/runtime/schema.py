"""What one model type declares, as a single immutable fact.

Every question the runtime asks about a type — which columns ``$select`` may name,
which navigations ``$expand`` may reach, which names the service assigns, which
Python attribute spells which wire name — is a projection of the same declarations.
Asked separately they became six class attributes and four loops over one dict;
asked as one object they are attributes of a fact built once, when the class is
created::

    Event._schema.columns  # the columns $select accepts
    Event._schema.navigations  # what $expand can reach
    Event._schema.readonly  # what a request may not send
    Event._schema.by_attr  # python attribute -> wire name
    Event._schema.declared_limits()  # the @limit declarations of the type and its members

The build is eager because a class body is complete by the time
``ClientObject.__init_subclass__`` runs. The other half of the model cannot be: a
``ClientValue`` declares its metadata in ``field(metadata=...)``, which only exists
after ``@dataclass`` has been applied, so
:func:`office365.runtime.types.odata_property.field_declarations` stays lazy. One
:class:`~office365.runtime.types.odata_property.ODataPropertyMeta`, two moments at
which it becomes readable — and the reason the two halves do not share a builder.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Dict, Mapping, Optional, Tuple

from office365.runtime.limits import Limit, LimitDecl, collect_class_limits, collect_limit_meta
from office365.runtime.types.odata_property import _ODATA_MARKER, ODataPropertyMeta

_EMPTY_MAP: Mapping = MappingProxyType({})


def _collect_properties(model: type) -> Dict[str, ODataPropertyMeta]:
    """The ``@odata`` declarations of ``model``, its base class's first.

    Returns a fresh dict: a subclass inherits its base class's declarations but must
    never be able to add one to them.
    """
    inherited = getattr(model, "_schema", None)
    properties: Dict[str, ODataPropertyMeta] = dict(inherited.properties) if inherited is not None else {}
    for attr_name, attr in model.__dict__.items():
        target = attr.fget if isinstance(attr, property) else attr
        declared: Optional[ODataPropertyMeta] = getattr(target, _ODATA_MARKER, None)
        if declared is not None:
            # The getter is the carrier of the declaration, so it is also the only
            # place that knows which attribute reads it.
            declared.attr = attr_name
            properties[declared.name] = declared
    return properties


@dataclass(frozen=True)
class TypeSchema:
    """The declarations of one model class.

    Immutable on purpose: a class fact that a consumer can edit is a class fact that
    drifts. The ``ODataPropertyMeta`` rows inside ``properties`` are shared with the
    class body that declared them (a getter carries its own row).
    """

    #: Wire name -> declaration, in declaration order (base class first).
    properties: Mapping[str, ODataPropertyMeta] = _EMPTY_MAP
    #: The wire names ``$select`` accepts: declarations that are not navigations.
    columns: Tuple[str, ...] = ()
    #: The wire names ``$expand`` can reach.
    navigations: Tuple[str, ...] = ()
    #: Python attribute name -> wire name, for the declared getters.
    by_attr: Mapping[str, str] = _EMPTY_MAP
    #: Wire names the service assigns: a response carries them, a request may not.
    readonly: frozenset[str] = frozenset()
    #: Wire names a request always sends, even when nobody set them.
    persistable: frozenset[str] = frozenset()
    #: The ``@limit`` declarations on the type itself, accumulated up the hierarchy: a
    #: subclass is subject to its base class's limits and its own.
    class_limits: Tuple[LimitDecl, ...] = ()
    #: Member name -> the ``@limit`` declarations carried by that method or property.
    member_limits: Mapping[str, Tuple[LimitDecl, ...]] = _EMPTY_MAP

    @classmethod
    def build(cls, model: type) -> TypeSchema:
        """Read the declarations of ``model``, inheriting its base class's."""
        properties = _collect_properties(model)
        member_limits = MappingProxyType(collect_limit_meta(model))
        by_attr: Dict[str, str] = {}
        for wire_name, declared in properties.items():
            if declared.attr:
                # First declaration wins, as the scan this replaces did: one getter can
                # be declared under more than one wire name.
                by_attr.setdefault(declared.attr, wire_name)
        return cls(
            properties=MappingProxyType(properties),
            columns=tuple(name for name, declared in properties.items() if not declared.navigation),
            navigations=tuple(name for name, declared in properties.items() if declared.navigation),
            by_attr=MappingProxyType(by_attr),
            readonly=frozenset(name for name, declared in properties.items() if declared.readonly),
            persistable=frozenset(name for name, declared in properties.items() if declared.persist),
            class_limits=collect_class_limits(model),
            member_limits=member_limits,
        )

    def declared_limits(self) -> Tuple[Limit, ...]:
        """Every limit the type is subject to: its own, then its members'."""
        return (
            *(decl.limit for decl in self.class_limits),
            *(decl.limit for decls in self.member_limits.values() for decl in decls),
        )


#: The schema of a type that declares nothing.
EMPTY = TypeSchema()
