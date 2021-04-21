from office365.runtime.client_value import ClientValue
from office365.sharepoint.base_entity import BaseEntity


class TenantWebTemplate(ClientValue):

    def __init__(self):
        super().__init__()

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.TenantAdministration.SPOTenantWebTemplate"


class TenantAdminEndpoints(BaseEntity):
    pass
