from office365.runtime.client_object import ClientObject
from office365.runtime.resource_path import ResourcePath


class Entity(ClientObject):

    @property
    def entity_type_name(self):
        return "microsoft.graph." + type(self).__name__

    @property
    def id(self):
        """The unique identifier of the drive.
        :rtype: str or None
        """
        if self.is_property_available("id"):
            return self.properties['id']
        return None

    def set_property(self, name, value, persist_changes=True):
        super(Entity, self).set_property(name, value, persist_changes)
        if name == "id" and self._resource_path is None:
            self._resource_path = ResourcePath(
                value,
                self._parent_collection.resource_path)
