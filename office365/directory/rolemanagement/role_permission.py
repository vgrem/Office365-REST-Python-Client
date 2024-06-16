from office365.directory.rolemanagement.resource_action import ResourceAction
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


class RolePermission(ClientValue):
    """ """

    def __init__(self, resourceActions=None):
        self.resourceActions = ClientValueCollection(ResourceAction, resourceActions)
