from office365.runtime.client_value_object import ClientValueObject
from office365.sharepoint.basePermissions import BasePermissions


class RoleDefinitionCreationInformation(ClientValueObject):

    def __init__(self):
        """Contains properties that are used as parameters to initialize a role definition."""
        super(RoleDefinitionCreationInformation, self).__init__()
        self.Name = None
        self.Description = None
        self.BasePermissions = BasePermissions()
