from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.tenant.administration.smtp_server import SmtpServer


class TenantAdminSettingsService(BaseEntity):

    @property
    def smtp_server(self):
        return self.properties.get("SmtpServer", SmtpServer())

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.TenantAdministration.TenantAdminSettingsService"
