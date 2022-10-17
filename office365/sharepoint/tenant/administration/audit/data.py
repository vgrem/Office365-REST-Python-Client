from office365.runtime.client_value import ClientValue


class AuditData(ClientValue):

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Administration.TenantAdmin.AuditData"
