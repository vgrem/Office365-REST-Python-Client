from office365.runtime.clientValue import ClientValue
from office365.sharepoint.permissions.basePermissions import BasePermissions


class RoleDefinitionCreationInformation(ClientValue):

    def __init__(self):
        """Contains properties that are used as parameters to initialize a role definition."""
        super(RoleDefinitionCreationInformation, self).__init__()
        self.Name = None
        self.Description = None
        self.BasePermissions = BasePermissions()
