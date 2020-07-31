from office365.runtime.client_value import ClientValue


class SitePropertiesEnumerableFilter(ClientValue):

    def __init__(self, _filter, start_index, include_detail):
        super().__init__()
        self.Filter = _filter
        # self.GroupIdDefined = None
        # self.IncludeDetail = include_detail
        # self.IncludePersonalSite = False
        # self.StartIndex = start_index
        # self.Template = None

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.TenantAdministration.SPOSitePropertiesEnumerableFilter"
