from office365.runtime.client_value import ClientValue


class HubSitePermission(ClientValue):

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.TenantAdministration.HubSitePermission"
