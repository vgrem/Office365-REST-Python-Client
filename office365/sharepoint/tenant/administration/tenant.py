from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.tenant.administration.hubSiteProperties import HubSiteProperties
from office365.sharepoint.tenant.administration.secondary_administrators_fields_data import \
    SecondaryAdministratorsFieldsData
from office365.sharepoint.tenant.administration.secondary_administrators_info import SecondaryAdministratorsInfo
from office365.sharepoint.tenant.administration.site_properties import SiteProperties
from office365.sharepoint.tenant.administration.sitePropertiesCollection import SitePropertiesCollection
from office365.sharepoint.tenant.administration.sitePropertiesEnumerableFilter import SitePropertiesEnumerableFilter
from office365.sharepoint.tenant.administration.spoOperation import SpoOperation


class Tenant(BaseEntity):

    def __init__(self, context):
        super().__init__(context, ResourcePath("Microsoft.Online.SharePoint.TenantAdministration.Tenant"),
                         "Microsoft.Online.SharePoint.TenantAdministration")

    def get_site_secondary_administrators(self, site_id):
        """
        Gets site collection administrators

        :type site_id: str
        """
        return_type = ClientValueCollection(SecondaryAdministratorsInfo)
        payload = SecondaryAdministratorsFieldsData(site_id)
        qry = ServiceOperationQuery(self, "GetSiteSecondaryAdministrators", None, payload,
                                    "secondaryAdministratorsFieldsData", return_type)
        self.context.add_query(qry)
        return return_type

    def set_site_secondary_administrators(self, site_id, emails, names=None):
        """
        Sets site collection administrators

        :type names: list[str] or None
        :type emails: list[str]
        :type site_id: str
        """
        payload = SecondaryAdministratorsFieldsData(site_id, emails, names)
        qry = ServiceOperationQuery(self, "SetSiteSecondaryAdministrators", None, payload,
                                    "secondaryAdministratorsFieldsData", None)
        self.context.add_query(qry)
        return self

    def register_hub_site(self, site_url):
        """
        Registers an existing site as a hub site.

        :param str site_url:
        :return:
        """
        return_type = HubSiteProperties(self.context)
        params = {"siteUrl": site_url}
        qry = ServiceOperationQuery(self, "RegisterHubSite", None, params, None, return_type)
        self.context.add_query(qry)
        return return_type

    def unregister_hub_site(self, siteUrl):
        """
        Unregisters a hub site so that it is no longer a hub site.

        :param str siteUrl:
        :return:
        """
        params = {"siteUrl": siteUrl}
        qry = ServiceOperationQuery(self, "UnregisterHubSite", None, params, None, None)
        self.context.add_query(qry)
        return self

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
    def root_site_url(self):
        """

        :rtype: str or None
        """
        return self.properties.get('RootSiteUrl', None)

    @property
    def _sites(self):
        """Gets a collection of sites."""
        if self.is_property_available('sites'):
            return self.properties['sites']
        else:
            return SitePropertiesCollection(self.context, ResourcePath("sites", self.resource_path))
