from __future__ import annotations

from datetime import datetime
from typing import Optional

from typing_extensions import Self

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.onedrive.internal.paths.children import ChildrenPath
from office365.onedrive.termstore.relation import Relation
from office365.onedrive.termstore.sets.name import LocalizedName
from office365.onedrive.termstore.terms.collection import TermCollection
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata


class Set(Entity):
    """
    Represents the set used in a term store. The set represents a unit which contains a collection of hierarchical
    terms. A group can contain multiple sets.
    """

    def __repr__(self):
        return repr(self.localized_names)

    def delete_object(self, *, ignore_missing: bool = False) -> Self:
        def _delete_set():
            super(Set, self).delete_object(ignore_missing=ignore_missing)

        def _on_terms_loaded(terms: TermCollection):
            if len(terms) == 0:
                _delete_set()
            else:
                for t in terms:
                    t.delete_object(ignore_missing=ignore_missing)
                self.after_execute(lambda _: _delete_set())

        self.children.expand(["children"]).get().after_execute(_on_terms_loaded)
        return self

    @property
    def children(self) -> TermCollection:
        """Children terms of set in term store."""
        return self.properties.get(
            "children",
            TermCollection(
                self.context,
                ChildrenPath(self.resource_path, self.terms.resource_path),
            ),
        )

    @odata(name="localizedNames")
    @property
    def localized_names(self) -> ClientValueCollection[LocalizedName]:
        """"""
        return self.properties.get("localizedNames", ClientValueCollection(LocalizedName))

    @property
    def display_name(self) -> str | None:
        if len(self.localized_names) > 0:
            return self.localized_names[0].name
        return None

    @odata(name="parentGroup")
    @property
    def parent_group(self):
        """The parent group that contains the set."""
        from office365.onedrive.termstore.groups.group import Group

        return self.properties.get(
            "parentGroup",
            Group(self.context, ResourcePath("parentGroup", self.resource_path)),
        )

    @property
    def relations(self) -> EntityCollection[Relation]:
        """Indicates which terms have been pinned or reused directly under the set."""
        return self.properties.get(
            "relations",
            EntityCollection(self.context, Relation, ResourcePath("relations", self.resource_path)),
        )

    @property
    def terms(self) -> TermCollection:
        """All the terms under the set."""
        return self.properties.get(
            "terms",
            TermCollection(self.context, ResourcePath("terms", self.resource_path)),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.termStore.set"

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)
