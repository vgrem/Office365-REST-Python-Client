from office365.runtime.client_object import ClientObject
from office365.runtime.resource_path import ResourcePath
from office365.sharepoint.taxonomy.term_collection import TermCollection


class TermSet(ClientObject):

    @property
    def terms(self):
        return self.properties.get("terms",
                                   TermCollection(self.context, ResourcePath("terms", self.resource_path)))

    def set_property(self, name, value, persist_changes=True):
        super(TermSet, self).set_property(name, value, persist_changes)
        if self._resource_path is None:
            if name == "id":
                self._resource_path = ResourcePath(value, self._parent_collection.resource_path)
        return self
