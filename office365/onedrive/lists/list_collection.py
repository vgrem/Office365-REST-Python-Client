from office365.entity_collection import EntityCollection
from office365.onedrive.lists.list import List
from office365.runtime.queries.create_entity import CreateEntityQuery


class ListCollection(EntityCollection):
    """Drive list's collection"""

    def __init__(self, context, resource_path=None):
        super(ListCollection, self).__init__(context, List, resource_path)

    def add(self, list_creation_information):
        """
        Creates a Drive list resource

        """
        target_list = List(self.context)
        self.add_child(target_list)
        qry = CreateEntityQuery(self, list_creation_information, target_list)
        self.context.add_query(qry)
        return target_list
