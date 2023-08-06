from office365.directory.object import DirectoryObject


class ResourceSpecificPermissionGrant(DirectoryObject):
    """
    Declares the permission that has been granted to a specific Azure AD app for an instance of a resource
    in Microsoft Graph.
    """

    @property
    def client_id(self):
        """ID of the Azure AD app that has been granted access. """
        return self.properties.get("clientId", None)

    @property
    def client_app_id(self):
        """ID of the service principal of the Azure AD app that has been granted access."""
        return self.properties.get("clientAppId", None)

    @property
    def permission(self):
        """The name of the resource-specific permission.
        :rtype: str
        """
        return self.properties.get("permission", None)

    @property
    def permission_type(self):
        """The type of permission. Possible values are: Application, Delegated. Read-only.
        :rtype: str
        """
        return self.properties.get("permissionType", None)

    @property
    def resource_app_id(self):
        """ID of the Azure AD app that is hosting the resource. Read-only.
        :rtype: str
        """
        return self.properties.get("resourceAppId", None)

