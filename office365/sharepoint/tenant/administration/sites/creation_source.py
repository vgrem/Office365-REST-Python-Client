from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.sharepoint.tenant.administration.sites.creation_data import SiteCreationData


class SiteCreationSource(ClientValue):

    def __init__(self, site_creation_data=None):
        self.SiteCreationData = ClientValueCollection(SiteCreationData, site_creation_data)

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.TenantAdministration.SiteCreationSource"
