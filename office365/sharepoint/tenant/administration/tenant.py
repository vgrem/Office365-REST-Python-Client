from office365.runtime.client_object import ClientObject
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.queries.update_entity_query import UpdateEntityQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.publishing.portal_health_status import PortalHealthStatus
from office365.sharepoint.tenant.administration.hubsite_properties import HubSiteProperties
from office365.sharepoint.tenant.administration.secondary_administrators_fields_data import \
    SecondaryAdministratorsFieldsData
from office365.sharepoint.tenant.administration.secondary_administrators_info import SecondaryAdministratorsInfo
from office365.sharepoint.tenant.administration.site_properties import SiteProperties
from office365.sharepoint.tenant.administration.site_properties_collection import SitePropertiesCollection
from office365.sharepoint.tenant.administration.sitePropertiesEnumerableFilter import SitePropertiesEnumerableFilter
from office365.sharepoint.tenant.administration.spo_operation import SpoOperation


class Tenant(ClientObject):
    """Represents a SharePoint tenant."""

    def __init__(self, context):
        super(Tenant, self).__init__(
            context,
            ResourcePath("Microsoft.Online.SharePoint.TenantAdministration.Tenant"),
            None,
            "Microsoft.Online.SharePoint.TenantAdministration"
            )

    def export_to_csv(self, view_xml=None):
        result = ClientResult(self.context)
        payload = {
            "viewXml": view_xml
        }
        qry = ServiceOperationQuery(self, "ExportToCSV", None, payload, None, result)
        self.context.add_query(qry)
        return result

    def update(self):
        """Update Tenant settings"""
        qry = UpdateEntityQuery(self)
        self.context.add_query(qry)
        return self

    @staticmethod
    def from_url(admin_site_url):
        """
        :type admin_site_url: str
        """
        from office365.sharepoint.client_context import ClientContext
        admin_client = ClientContext(admin_site_url)
        return Tenant(admin_client)

    def get_lock_state_by_id(self, site_id):
        return self._sites.get_lock_state_by_id(site_id)

    def hub_sites(self, site_url):
        pass

    def check_tenant_licenses(self, licenses):
        """
        Checks whether a tenant has the specified licenses.

        :param list[str] licenses: The list of licenses to check for.
        :return:
        """
        result = ClientResult(self.context)
        params = ClientValueCollection(str, licenses)
        qry = ServiceOperationQuery(self, "CheckTenantLicenses", None, params, "licenses", result)
        self.context.add_query(qry)
        return result

    def get_site_health_status(self, source_url):
        """
        :type source_url: str
        """
        result = ClientResult(self.context, PortalHealthStatus())
        params = {"sourceUrl": source_url}
        qry = ServiceOperationQuery(self, "GetSiteHealthStatus", None, params, None, result)
        self.context.add_query(qry)
        return result

    def get_site_secondary_administrators(self, site_id):
        """
        Gets site collection administrators

        :type site_id: str
        """
        result = ClientResult(self.context, ClientValueCollection(SecondaryAdministratorsInfo))
        payload = SecondaryAdministratorsFieldsData(site_id)
        qry = ServiceOperationQuery(self, "GetSiteSecondaryAdministrators", None, payload,
                                    "secondaryAdministratorsFieldsData", result)
        self.context.add_query(qry)
        return result

    def set_site_secondary_administrators(self, site_id, emails=None, names=None):
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

    def unregister_hub_site(self, site_url):
        """
        Unregisters a hub site so that it is no longer a hub site.

        :param str site_url:
        :return:
        """
        params = {"siteUrl": site_url}
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
        """Permanently removes the specified deleted site from the recycle bin.

        :param str site_url: A string representing the URL of the site.
        """
        result = SpoOperation(self.context)
        qry = ServiceOperationQuery(self, "RemoveDeletedSite", [site_url], None, None, result)
        self.context.add_query(qry)
        return result

    def restore_deleted_site(self, site_url):
        """Restores deleted site with the specified URL

        :param str site_url: A string representing the URL of the site.
        """
        result = SpoOperation(self.context)
        qry = ServiceOperationQuery(self, "RestoreDeletedSite", [site_url], None, None, result)
        self.context.add_query(qry)
        return result

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

    def connect_site_to_hub_site_by_id(self, site_url, hub_site_id):
        """

        :param str site_url:
        :param str hub_site_id:
        :return:
        """
        params = {
            "siteUrl": site_url,
            "hubSiteId": hub_site_id
        }
        qry = ServiceOperationQuery(self, "ConnectSiteToHubSiteById", None, params, None, None)
        self.context.add_query(qry)
        return self

    @property
    def root_site_url(self):
        """

        :rtype: str or None
        """
        return self.properties.get('RootSiteUrl', None)

    @property
    def _sites(self):
        """Gets a collection of sites."""
        return self.properties.get('sites',
                                   SitePropertiesCollection(self.context, ResourcePath("sites", self.resource_path)))
