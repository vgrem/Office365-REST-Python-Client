from office365.runtime.client_value import ClientValue


class TenantWebTemplate(ClientValue):

    def __init__(self):
        super(TenantWebTemplate, self).__init__()

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.TenantAdministration.SPOTenantWebTemplate"
