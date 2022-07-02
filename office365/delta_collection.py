from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath


class DeltaCollection(EntityCollection):

    @property
    def delta(self):
        """
        Get newly created, updated, or deleted entities (changes)
        """
        return self.properties.get('delta',
                                   DeltaCollection(self.context, self._item_type,
                                                   ResourcePath("delta", self.resource_path)))
