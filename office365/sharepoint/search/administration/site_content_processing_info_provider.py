from office365.sharepoint.base_entity import BaseEntity


class SiteContentProcessingInfoProvider(BaseEntity):

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Client.Search.Administration.SiteContentProcessingInfoProvider"
