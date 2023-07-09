from office365.runtime.client_object import ClientObject
from office365.runtime.paths.entity import EntityPath
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.delete_entity import DeleteEntityQuery
from office365.runtime.queries.update_entity import UpdateEntityQuery


class Entity(ClientObject):
    """Base entity"""

    def update(self):
        """Updates the entity."""
        qry = UpdateEntityQuery(self)
        self.context.add_query(qry)
        return self

    def delete_object(self):
        """Deletes the entity."""
        qry = DeleteEntityQuery(self)
        self.context.add_query(qry)
        self.remove_from_parent_collection()
        return self

    @property
    def context(self):
        """
        :rtype: office365.graph_client.GraphClient
        """
        return self._context

    @property
    def entity_type_name(self):
        if self._entity_type_name is None:
            name = type(self).__name__
            self._entity_type_name = "microsoft.graph." + name[0].lower() + name[1:]
        return self._entity_type_name

    @property
    def id(self):
        """The unique identifier of the entity.
        :rtype: str or None
        """
        return self.properties.get('id', None)

    @property
    def property_ref_name(self):
        return "id"

    def set_property(self, name, value, persist_changes=True):
        super(Entity, self).set_property(name, value, persist_changes)
        if name == self.property_ref_name:
            if self._resource_path is None:
                if isinstance(self.parent_collection.resource_path, EntityPath):
                    self._resource_path = self.parent_collection.resource_path.patch(value)
                else:
                    self._resource_path = ResourcePath(value, self.parent_collection.resource_path)
            else:
                self._resource_path.patch(value, inplace=True)
        return self
