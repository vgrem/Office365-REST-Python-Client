from office365.sharepoint.base_entity_collection import BaseEntityCollection


class HashTagCollection(BaseEntityCollection):
    """The HashTagCollection class specifies a collection of HashTags. For information about the HashTag type,
    see section 3.1.5.55"""

    def set_property(self, name, value, persist_changes=False):
        if name == "Items":
            self._data = list(value.values())
        else:
            super(HashTagCollection, self).set_property(name, value)
        return self
