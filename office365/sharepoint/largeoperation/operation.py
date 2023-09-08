from office365.sharepoint.base_entity import BaseEntity


class SPLargeOperation(BaseEntity):

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.LargeOperation.SPLargeOperation"
