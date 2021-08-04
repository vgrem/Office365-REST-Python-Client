from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.queries.create_entity_query import CreateEntityQuery
from office365.runtime.resource_path import ResourcePath


class EntityCollection(ClientObjectCollection):

    def __getitem__(self, key):
        """

        :param key: key is used to address a Entity resource by either an index in collection
        or by resource id
        :type key: int or str
        :rtype: EntityCollection
        """
        if type(key) == int:
            return super(EntityCollection, self).__getitem__(key)
        return self._item_type(self.context, ResourcePath(key, self.resource_path))

    def new(self, **kwargs):
        return self.create_typed_object(properties=kwargs, persist_changes=True)

    def add(self, **kwargs):
        """Creates a resource

        :rtype: office365.entity.Entity
        """
        return_type = self.new()
        self.add_child(return_type)
        qry = CreateEntityQuery(self, kwargs, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def context(self):
        """
        :rtype: office365.graph_client.GraphClient
        """
        return self._context
