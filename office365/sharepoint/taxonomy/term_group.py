from office365.runtime.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.taxonomy.termSetCollection import TermSetCollection


class TermGroup(BaseEntity):
    """Represents the top-level container in a TermStore object."""

    @property
    def termSets(self):
        return self.properties.get("termSets",
                                   TermSetCollection(self.context, ResourcePath("termSets", self.resource_path)))

    def set_property(self, name, value, persist_changes=True):
        super(TermGroup, self).set_property(name, value, persist_changes)
        if self._resource_path is None:
            if name == "id":
                self._resource_path = ResourcePath(value, self._parent_collection.resource_path)
        return self
