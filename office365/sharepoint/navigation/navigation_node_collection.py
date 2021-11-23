from office365.runtime.queries.create_entity_query import CreateEntityQuery
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.navigation.navigation_node import NavigationNode


class NavigationNodeCollection(BaseEntityCollection):

    def __init__(self, context, resource_path=None):
        super(NavigationNodeCollection, self).__init__(context, NavigationNode, resource_path)

    def add(self, create_node_info):
        """
        Creates a navigation node object and adds it to the collection.

        :type create_node_info: office365.sharepoint.navigation.navigation_node_creation_information.NavigationNodeCreationInformation
        """
        target_node = NavigationNode(self.context)
        target_node.title = create_node_info.Title
        target_node.url = create_node_info.Url
        self.add_child(target_node)
        qry = CreateEntityQuery(self, target_node, target_node)
        self.context.add_query(qry)
        return target_node

    def get_by_index(self, index):
        target_node = NavigationNode(self.context)
        self.add_child(target_node)
        qry = ServiceOperationQuery(self, "GetByIndex", [index], None, None, target_node)
        self.context.add_query(qry)
        return target_node

    def get_by_id(self, node_id):
        """Gets the navigation node with the specified ID.

        :type node_id: str
        """
        return NavigationNode(self.context,
                              ServiceOperationPath("GetById", [node_id], self.resource_path))
