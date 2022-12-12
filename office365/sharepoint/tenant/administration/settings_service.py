from office365.runtime.client_result import ClientResult
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import StringCollection
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.tenant.administration.smtp_server import SmtpServer


class TenantAdminSettingsService(BaseEntity):

    def __init__(self, context):
        static_path = ResourcePath("Microsoft.Online.SharePoint.TenantAdministration.TenantAdminSettingsService")
        super(TenantAdminSettingsService, self).__init__(context, static_path)

    def get_tenant_sharing_status(self):
        return_type = ClientResult(self.context, int())
        qry = ServiceOperationQuery(self, "GetTenantSharingStatus", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def available_managed_paths_for_site_creation(self):
        return self.properties.get("AvailableManagedPathsForSiteCreation", StringCollection())

    @property
    def smtp_server(self):
        return self.properties.get("SmtpServer", SmtpServer())

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.TenantAdministration.TenantAdminSettingsService"

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "AvailableManagedPathsForSiteCreation": self.available_managed_paths_for_site_creation,
                "SmtpServer": self.smtp_server
            }
            default_value = property_mapping.get(name, None)
        return super(TenantAdminSettingsService, self).get_property(name, default_value)
