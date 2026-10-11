from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.onedrive.internal.paths.children import ChildrenPath
from office365.onedrive.termstore.terms.description import LocalizedDescription
from office365.onedrive.termstore.terms.label import LocalizedLabel
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.onedrive.termstore.terms.collection import TermCollection


class Term(Entity):
    """Represents a term used in a term store. A term can be used to represent an object which can then
    be used as a metadata to tag content. Multiple terms can be organized in a hierarchical manner within a set.
    """

    @property
    def descriptions(self):
        """Description about term that is dependent on the languageTag."""
        return self.properties.get("descriptions", ClientValueCollection(LocalizedDescription))

    @property
    def labels(self):
        """Label metadata for a term."""
        return self.properties.get("labels", ClientValueCollection(LocalizedLabel))

    @property
    def display_name(self) -> str | None:
        if len(self.labels) > 0:
            default = next((lbl for lbl in self.labels if lbl.isDefault), self.labels[0])
            return default.name
        return None

    @property
    def created_datetime(self) -> datetime:
        """Timestamp at which the term was created."""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def children(self) -> TermCollection:
        """Children of current term."""
        from office365.onedrive.termstore.terms.collection import TermCollection

        assert self.resource_path is not None and self.resource_path.parent is not None
        return self.properties.get(
            "children",
            TermCollection(
                self.context,
                ChildrenPath(self.resource_path, self.resource_path.parent),
                self,
            ),
        )

    @property
    def relations(self):
        """To indicate which terms are related to the current term as either pinned or reused."""
        from office365.onedrive.termstore.relation import Relation

        return self.properties.get(
            "relations",
            EntityCollection(self.context, Relation, ResourcePath("relations", self.resource_path)),
        )

    @property
    def set(self):
        """The set in which the term is created."""
        from office365.onedrive.termstore.sets.set import Set

        return self.properties.get("set", Set(self.context, ResourcePath("set", self.resource_path)))

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.termStore.term"

    @property
    def last_modified_date_time(self) -> Optional[datetime]:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)
