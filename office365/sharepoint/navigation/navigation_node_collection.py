from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.queries.create_entity_query import CreateEntityQuery
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.sharepoint.navigation.navigation_node import NavigationNode


class NavigationNodeCollection(ClientObjectCollection):

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

    def get_by_id(self, node_id):
        """Gets the navigation node with the specified ID.

        :type node_id: str
        """
        return NavigationNode(self.context,
                              ResourcePathServiceOperation("GetById", [node_id], self.resource_path))
