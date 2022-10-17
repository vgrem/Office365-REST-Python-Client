from office365.runtime.client_value import ClientValue


class UnifiedAuditRecord(ClientValue):

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Administration.TenantAdmin.UnifiedAuditRecord"
