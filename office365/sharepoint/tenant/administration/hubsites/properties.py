from office365.runtime.client_value_collection import ClientValueCollection
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.tenant.administration.hubsites.permission import HubSitePermission


class HubSiteProperties(BaseEntity):

    @property
    def permissions(self):
        return self.properties.get("Permissions", ClientValueCollection(HubSitePermission))

    @property
    def site_id(self):
        """
        Returns the Site identifier

        :rtype: str or None
        """
        return self.properties.get("SiteId", None)

    @property
    def property_ref_name(self):
        return "SiteId"

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.TenantAdministration.HubSiteProperties"
