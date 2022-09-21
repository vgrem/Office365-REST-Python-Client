from office365.sharepoint.base_entity import BaseEntity


class SharePointHomeServiceContext(BaseEntity):
    """
    This data type is reserved for future use and MUST NOT be used by the protocol implementation.
    """

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Portal.SharePointHomeServiceContext"
