from office365.runtime.client_value import ClientValue


class SiteInfoForSitePicker(ClientValue):

    def __init__(self, site_name=None):
        self.SiteName = site_name

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.TenantAdministration.SiteInfoForSitePicker"
