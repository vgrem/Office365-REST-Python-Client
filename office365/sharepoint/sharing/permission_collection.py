from office365.runtime.client_value import ClientValue


class PermissionCollection(ClientValue):
    """
    This class is returned when Microsoft.SharePoint.Client.Sharing.SecurableObjectExtensions.GetSharingInformation
    is called with the optional expand on permissionsInformation property. It contains a collection of LinkInfo and
    PrincipalInfo objects of users/groups that have access to the list item and also the site administrators who have
    implicit access.
    """

    @property
    def entity_type_name(self):
        return "SP.Sharing.PermissionCollection"
