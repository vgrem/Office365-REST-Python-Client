from office365.graph.onedrive.list import List
from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_query import CreateEntityQuery


class ListCollection(ClientObjectCollection):
    """Drive list's collection"""

    def __init__(self, context, resource_path=None):
        super(ListCollection, self).__init__(context, List, resource_path)

    def add(self, list_creation_information):
        """Creates a Drive list resource"""
        target_list = List(self.context)
        self.add_child(target_list)
        qry = CreateEntityQuery(self, list_creation_information, target_list)
        self.context.add_query(qry)
        return target_list
