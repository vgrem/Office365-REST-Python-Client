from office365.runtime.client_object_collection import ClientObjectCollection
from office365.sharepoint.permissions.roleDefinition import RoleDefinition


class RoleDefinitionCollection(ClientObjectCollection):

    def __init__(self, context, resource_path=None):
        super(RoleDefinitionCollection, self).__init__(context, RoleDefinition, resource_path)
