from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    from office365.onedrive.termstore.relation_type import RelationType
    from office365.onedrive.termstore.sets.set import Set


class Relation(Entity):
    """
    Represents the relationship between terms in a term store.
    Currently, two types of relationships are supported: pin and reuse.

    In a pin relationship, a term can be pinned under a different term in a different term set.
    In a pinned relationship, new children to the term can only be added in the term set in which the term was created.
    Any change in the hierarchy under the term is reflected across the sets in which the term was pinned.

    The reuse relationship is similar to the pinned relationship except that changes to the reused term can be made
    from any hierarchy in which the term is reused. Also, a change in hierarchy made to the reused term doesn't get
    reflected in the other term sets in which the term is reused.
    """

    @odata(name="fromTerm")
    @property
    def from_term(self):
        """The from term of the relation. The term from which the relationship is defined.
        A null value would indicate the relation is directly with the set."""
        from office365.onedrive.termstore.terms.term import Term

        return self.properties.get("fromTerm", Term(self.context, ResourcePath("fromTerm", self.resource_path)))

    @odata(name="toTerm")
    @property
    def to_term(self):
        """The to term of the relation. The term to which the relationship is defined."""
        from office365.onedrive.termstore.terms.term import Term

        return self.properties.get("toTerm", Term(self.context, ResourcePath("toTerm", self.resource_path)))

    @property
    def set(self):
        """The set in which the relation is relevant."""
        from office365.onedrive.termstore.sets.set import Set

        return self.properties.get("set", Set(self.context, ResourcePath("set", self.resource_path)))

    @property
    def set_(self) -> Set:
        from office365.onedrive.termstore.sets.set import Set

        """Gets the set property"""
        return self.properties.get("set", Set(self.context, ResourcePath("set", self.resource_path)))

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.termStore.Relation"

    @property
    def relationship(self) -> RelationType:
        """Gets the relationship property"""
        from office365.onedrive.termstore.relation_type import RelationType

        return self.properties.get("relationship", RelationType.pin)
