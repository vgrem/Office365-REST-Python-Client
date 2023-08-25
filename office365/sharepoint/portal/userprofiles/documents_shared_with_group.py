from office365.sharepoint.base_entity import BaseEntity


class DocumentsSharedWithGroup(BaseEntity):
    """
    Provides methods for working with a list that shares documents with a SharePoint Group on the user's personal site.
    """

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Portal.UserProfiles.DocumentsSharedWithGroup"
