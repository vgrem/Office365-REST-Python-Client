from office365.runtime.client_object import ClientObject
from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.paths.resource_path import ResourcePath


class TaxonomyItem(ClientObject):

    def set_property(self, name, value, persist_changes=True):
        super(TaxonomyItem, self).set_property(name, value, persist_changes)
        if self._resource_path is None:
            if name == "id":
                self._resource_path = ResourcePath(value, self._parent_collection.resource_path)
        return self


class TaxonomyItemCollection(ClientObjectCollection):

    def __init__(self, context, taxonomy_item_type, resource_path=None):
        super(TaxonomyItemCollection, self).__init__(context, taxonomy_item_type, resource_path)
