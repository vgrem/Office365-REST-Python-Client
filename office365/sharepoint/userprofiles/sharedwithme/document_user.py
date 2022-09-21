from office365.runtime.client_value import ClientValue


class SharedWithMeDocumentUser(ClientValue):
    """Represents a user of a document that is shared with the current user."""

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Portal.UserProfiles.SharedWithMeDocumentUser"
