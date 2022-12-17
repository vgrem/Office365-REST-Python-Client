from office365.sharepoint.base_entity import BaseEntity


class UnifiedGroup(BaseEntity):

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.MultiGeo.Service.UnifiedGroup"
