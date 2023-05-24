from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.compat import is_string_type
from office365.runtime.paths.item import ItemPath
from office365.runtime.queries.create_entity import CreateEntityQuery
from office365.runtime.paths.resource_path import ResourcePath


class EntityCollection(ClientObjectCollection):
    """A collection container which represents a named collections of entities"""

    def __getitem__(self, key):
        """
        :param key: key is used to address an entity by either an index or by identifier
        :type key: int or str
        """
        if type(key) == int:
            return super(EntityCollection, self).__getitem__(key)
        elif is_string_type(key):
            return self.create_typed_object(resource_path=ResourcePath(key, self.resource_path))
        else:
            raise ValueError("Invalid key: expected either an entity index [int] or identifier [str]")

    def add(self, **kwargs):
        """
        Creates an entity and prepares the query
        """
        return_type = self.create_typed_object(kwargs, ItemPath(self.resource_path))
        self.add_child(return_type)
        qry = CreateEntityQuery(self, return_type, return_type)
        self.context.add_query(qry)
        return return_type

    def _find_by_unique_prop(self, name, val):
        """Retrieves entity by unique identifier

        :param str name: Property name
        :param str val: Property value
        """
        return_type = self.create_typed_object()
        self.add_child(return_type)
        filter_text = "{0} eq '{1}'".format(name, val)

        def _after_loaded(col):
            """
            :type col: EntityCollection
            """
            if len(col) != 1:
                message = "Not found or ambiguous match found for filter: {0}".format(filter_text)
                raise ValueError(message)
            return_type.set_property("id", col[0].get_property("id"))

        self.filter(filter_text)
        self.context.load(self, after_loaded=_after_loaded)
        return return_type

    @property
    def context(self):
        """
        :rtype: office365.graph_client.GraphClient
        """
        return self._context
