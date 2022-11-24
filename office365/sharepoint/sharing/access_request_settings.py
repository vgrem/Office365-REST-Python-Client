from office365.runtime.client_value import ClientValue


class AccessRequestSettings(ClientValue):
    """
    This class returns the access request settings. It’s an optional property that can be retrieved in
    Microsoft.SharePoint.Client.Sharing.SecurableObjectExtensions.GetSharingInformation() call on a list item.
    """

    @property
    def entity_type_name(self):
        return "SP.Sharing.AccessRequestSettings"
