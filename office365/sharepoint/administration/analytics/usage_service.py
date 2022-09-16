from office365.sharepoint.base_entity import BaseEntity


class SPAnalyticsUsageService(BaseEntity):

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Administration.SPAnalyticsUsageService"
