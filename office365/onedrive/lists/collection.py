from office365.entity_collection import EntityCollection
from office365.onedrive.lists.list import List
from office365.runtime.queries.create_entity import CreateEntityQuery


class ListCollection(EntityCollection):
    """Drive list's collection"""

    def __init__(self, context, resource_path=None):
        super(ListCollection, self).__init__(context, List, resource_path)

    def __getitem__(self, key):
        """
        Gets List by it's identifier or name
        :param str key: List identifier or name
        :rtype: List
        """
        return super(ListCollection, self).__getitem__(key)

    def add(self, creation_information):
        """
        Creates a Drive list resource

        :param Any creation_information:
        """
        return_type = List(self.context)
        self.add_child(return_type)
        qry = CreateEntityQuery(self, creation_information, return_type)
        self.context.add_query(qry)
        return return_type
