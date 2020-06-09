from office365.runtime.resource_path import ResourcePath
from office365.runtime.serviceOperationQuery import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.tenantadministration.siteProperties import SiteProperties
from office365.sharepoint.tenantadministration.sitePropertiesCollection import SitePropertiesCollection


class Tenant(BaseEntity):

    def __init__(self, context):
        super().__init__(context, ResourcePath("Microsoft.Online.SharePoint.TenantAdministration.Tenant"),
                         "Microsoft.Online.SharePoint.TenantAdministration")

    def get_site_properties_by_url(self, url, include_detail):
        """

        :param str url: A string that represents the site URL.
        :param bool include_detail: A Boolean value that indicates whether to include all of the SPSite properties.
        """
        site_props = SiteProperties(self.context)
        self._sites.add_child(site_props)
        payload = {
            'url': url,
            'includeDetail': include_detail
        }
        qry = ServiceOperationQuery(self, "getSitePropertiesByUrl", None, payload, None, site_props)
        self.context.add_query(qry)
        return site_props

    @property
    def _sites(self):
        """Gets a collection of sites."""
        if self.is_property_available('sites'):
            return self.properties['sites']
        else:
            return SitePropertiesCollection(self.context, ResourcePath("sites", self.resource_path))
