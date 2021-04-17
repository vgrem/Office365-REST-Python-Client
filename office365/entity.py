from office365.runtime.client_object import ClientObject
from office365.runtime.queries.delete_entity_query import DeleteEntityQuery
from office365.runtime.queries.update_entity_query import UpdateEntityQuery
from office365.runtime.resource_path import ResourcePath


class Entity(ClientObject):

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
        :rtype: office365.graph.graph_client.GraphClient
        """
        return self._context

    @property
    def entity_type_name(self):
        return "microsoft.graph." + type(self).__name__

    @property
    def id(self):
        """The unique identifier of the drive.
        :rtype: str or None
        """
        return self.properties.get('id', None)

    def set_property(self, name, value, persist_changes=True):
        super(Entity, self).set_property(name, value, persist_changes)
        if name == "id" and self._resource_path is None:
            self._resource_path = ResourcePath(
                value,
                self._parent_collection.resource_path)
        return self
