from office365.runtime.client_value import ClientValue


class SiteCreationDefaultStorageQuota(ClientValue):

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.TenantAdministration.SiteCreationDefaultStorageQuota"
