from office365.sharepoint.base_entity import BaseEntity


class TenantAdminEndpoints(BaseEntity):

    @property
    def o365_admin_center_endpoint(self):
        """
        :rtype: str or None
        """
        return self.properties.get("O365AdminCenterEndpoint", None)

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.TenantAdministration.TenantAdminEndpoints"
