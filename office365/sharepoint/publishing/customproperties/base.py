from office365.sharepoint.base_entity import BaseEntity


class BaseCustomProperty(BaseEntity):
    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Publishing.RestOnly.BaseCustomProperty"
