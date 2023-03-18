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

