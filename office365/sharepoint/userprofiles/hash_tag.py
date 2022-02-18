from office365.sharepoint.base_entity_collection import BaseEntityCollection


class HashTagCollection(BaseEntityCollection):

    def set_property(self, name, value, persist_changes=False):
        if name == "Items":
            self._data = list(value.values())
        else:
            super(HashTagCollection, self).set_property(name, value)
        return self
