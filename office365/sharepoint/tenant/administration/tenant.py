from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.tenant.administration.siteProperties import SiteProperties
from office365.sharepoint.tenant.administration.sitePropertiesCollection import SitePropertiesCollection
from office365.sharepoint.tenant.administration.sitePropertiesEnumerableFilter import SitePropertiesEnumerableFilter
from office365.sharepoint.tenant.administration.spoOperation import SpoOperation


class Tenant(BaseEntity):

    def __init__(self, context):
        super().__init__(context, ResourcePath("Microsoft.Online.SharePoint.TenantAdministration.Tenant"),
                         "Microsoft.Online.SharePoint.TenantAdministration")

    def create_site(self, site_create_props):
        """Queues a site collection for creation with the specified properties.

        :param SiteCreationProperties site_create_props:
        A SiteCreationProperties object that contains the initial properties
        of the new site collection.
        """
        result = SpoOperation(self.context)
        qry = ServiceOperationQuery(self, "CreateSite", None, site_create_props, "siteCreationProperties", result)
        self.context.add_query(qry)
        return result

    def remove_site(self, site_url):
        """Deletes the site with the specified URL

        :param str site_url: A string representing the URL of the site.
        """
        result = SpoOperation(self.context)
        qry = ServiceOperationQuery(self, "removeSite", [site_url], None, None, result)
        self.context.add_query(qry)
        return result

    def remove_deleted_site(self, site_url):
        pass

    def restore_deleted_site(self, site_url):
        pass

    def set_site_secondary_administrators(self, data):
        """

        :type data: SecondaryAdministratorsFieldsData
        """
        pass

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

    def get_site_properties_from_sharepoint_by_filters(self, _filter, start_index=0, include_detail=False):
        """

        :param bool include_detail:
        :param int start_index:
        :param str _filter:
        """
        site_props_col = SitePropertiesCollection(self.context)
        qry = ServiceOperationQuery(self, "getSitePropertiesFromSharePointByFilters",
                                    None,
                                    SitePropertiesEnumerableFilter(_filter, start_index, include_detail),
                                    "speFilter",
                                    site_props_col)
        self.context.add_query(qry)
        return site_props_col

    @property
    def _sites(self):
        """Gets a collection of sites."""
        if self.is_property_available('sites'):
            return self.properties['sites']
        else:
            return SitePropertiesCollection(self.context, ResourcePath("sites", self.resource_path))
