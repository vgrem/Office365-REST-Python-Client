from office365.runtime.client_object import ClientObject
from office365.runtime.resource_path import ResourcePath


class TermSet(ClientObject):

    def set_property(self, name, value, persist_changes=True):
        super(TermSet, self).set_property(name, value, persist_changes)
        if self._resource_path is None:
            if name == "id":
                self._resource_path = ResourcePath(value, self._parent_collection.resource_path)
        return self
