from office365.sharepoint.base_entity import BaseEntity


class TenantCrawlVersionsInfoProvider(BaseEntity):
    """"""

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Client.Search.Administration.TenantCrawlVersionsInfoProvider"
