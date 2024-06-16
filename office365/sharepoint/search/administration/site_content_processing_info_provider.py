from office365.sharepoint.entity import Entity


class SiteContentProcessingInfoProvider(Entity):
    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Client.Search.Administration.SiteContentProcessingInfoProvider"
