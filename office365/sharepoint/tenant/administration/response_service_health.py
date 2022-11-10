from office365.sharepoint.base_entity import BaseEntity


class ResponseServiceHealth(BaseEntity):

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.TenantAdministration.ResponseServiceHealth"
