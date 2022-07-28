import time

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.listitems.collection import ListItemCollection
from office365.sharepoint.publishing.portal_health_status import PortalHealthStatus
from office365.sharepoint.sites.home_sites_details import HomeSitesDetails
from office365.sharepoint.sites.site import Site
from office365.sharepoint.tenant.administration.hubsite_properties import HubSiteProperties
from office365.sharepoint.tenant.administration.secondary_administrators_fields_data import \
    SecondaryAdministratorsFieldsData
from office365.sharepoint.tenant.administration.secondary_administrators_info import SecondaryAdministratorsInfo
from office365.sharepoint.tenant.administration.site_creation_properties import SiteCreationProperties
from office365.sharepoint.tenant.administration.site_properties import SiteProperties
from office365.sharepoint.tenant.administration.site_properties_collection import SitePropertiesCollection
from office365.sharepoint.tenant.administration.sitePropertiesEnumerableFilter import SitePropertiesEnumerableFilter
from office365.sharepoint.tenant.administration.spo_operation import SpoOperation


class Tenant(BaseEntity):
    """Represents a SharePoint tenant."""

    def __init__(self, context):
        static_path = ResourcePath("Microsoft.Online.SharePoint.TenantAdministration.Tenant")
        super(Tenant, self).__init__(context, static_path)

    def get_home_sites(self):
        return_type = ClientResult(self.context, ClientValueCollection(HomeSitesDetails))
        qry = ServiceOperationQuery(self, "GetHomeSites", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_home_sites_details(self):
        return_type = ClientResult(self.context, ClientValueCollection(HomeSitesDetails))
        qry = ServiceOperationQuery(self, "GetHomeSitesDetails", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def export_to_csv(self, view_xml=None):
        result = ClientResult(self.context)
        payload = {
            "viewXml": view_xml
        }
        qry = ServiceOperationQuery(self, "ExportToCSV", None, payload, None, result)
        self.context.add_query(qry)
        return result

    @staticmethod
    def from_url(admin_site_url):
        """
        :type admin_site_url: str
        """
        from office365.sharepoint.client_context import ClientContext
        admin_client = ClientContext(admin_site_url)
        return Tenant(admin_client)

    def get_lock_state_by_id(self, site_id):
        return self.sites.get_lock_state_by_id(site_id)

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

    def get_site_status(self, url):
        """
        :param str url:
        """
        result = self.aggregated_site_collections_list.items.filter("SiteUrl eq '{0}'".format(url)).get()
        return result

    def get_sites_by_state(self, states=None):
        """
        :param list[int] states:
        """
        return_type = ListItemCollection(self.context,
                                         ResourcePath("items", self.aggregated_site_collections_list.resource_path))
        payload = {"states": states}
        qry = ServiceOperationQuery(self, "GetSitesByState", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

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

        :param str site_url: Site Url
        """
        payload = {"siteUrl": site_url}
        qry = ServiceOperationQuery(self, "UnregisterHubSite", None, payload, None, None)
        self.context.add_query(qry)
        return self

    def create_site(self, url, owner, title=None):
        """Queues a site collection for creation with the specified properties.

        :param str title: Sets the new site’s title.
        :param str url: Sets the new site’s URL.
        :param str owner: Sets the login name of the owner of the new site.
        """
        return_type = SpoOperation(self.context)
        payload = SiteCreationProperties(title=title, url=url, owner=owner)
        qry = ServiceOperationQuery(self, "CreateSite", None, payload, "siteCreationProperties", return_type)
        self.context.add_query(qry)
        return return_type

    def create_site_sync(self, url, owner, title=None):
        """Creates a site collection

         :param str title: Sets the new site’s title.
        :param str url: Sets the new site’s URL.
        :param str owner: Sets the login name of the owner of the new site.
        """
        return_type = Site(self.context)
        op = self.create_site(url, owner, title)

        def _verify_site_status(resp, items=None):
            """
            :type resp: requests.Response
            """
            if items is None:
                is_complete = op.is_complete
            else:
                is_complete = len([item for item in items if item.properties.get("SiteUrl") == url]) > 0
            if not is_complete:
                time.sleep(op.polling_interval_secs)
                items = self.get_sites_by_state([0, 1, 2])
                self.context.after_execute(_verify_site_status, items=items)

            return_type.set_property("__siteUrl", url)
        self.context.after_execute(_verify_site_status)
        return return_type

    def remove_site(self, site_url):
        """Deletes the site with the specified URL

        :param str site_url: A string representing the URL of the site.
        """
        result = SpoOperation(self.context)
        params = {"siteUrl": site_url}
        qry = ServiceOperationQuery(self, "removeSite", None, params, None, result)
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

    def get_site_properties_by_url(self, url, include_detail=False):
        """

        :param str url: A string that represents the site URL.
        :param bool include_detail: A Boolean value that indicates whether to include all of the SPSite properties.
        """
        return_type = SiteProperties(self.context)
        self.sites.add_child(return_type)
        payload = {
            'url': url,
            'includeDetail': include_detail
        }
        qry = ServiceOperationQuery(self, "getSitePropertiesByUrl", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_site_properties_from_sharepoint_by_filters(self, _filter, start_index=0, include_detail=False):
        """

        :param bool include_detail:
        :param int start_index:
        :param str _filter:
        """
        return_type = SitePropertiesCollection(self.context)
        qry = ServiceOperationQuery(self, "getSitePropertiesFromSharePointByFilters",
                                    None,
                                    SitePropertiesEnumerableFilter(_filter, start_index, include_detail),
                                    "speFilter",
                                    return_type)
        self.context.add_query(qry)
        return return_type

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
    def aggregated_site_collections_list(self):
        return self.context.web.lists.get_by_title("DO_NOT_DELETE_SPLIST_TENANTADMIN_AGGREGATED_SITECOLLECTIONS")

    @property
    def allow_comments_text_on_email_enabled(self):
        """
        When enabled, the email notification that a user receives when is mentioned,
            includes the surrounding document context

        :rtype: bool or None
        """
        return self.properties.get('AllowCommentsTextOnEmailEnabled', None)

    @property
    def allow_everyone_except_external_users_claim_in_private_site(self):
        """
        :rtype: bool or None
        """
        return self.properties.get('AllowEveryoneExceptExternalUsersClaimInPrivateSite', None)

    @property
    def allow_editing(self):
        """
        Prevents users from editing Office files in the browser and copying and pasting Office file contents
        out of the browser window.

        :rtype: bool or None
        """
        return self.properties.get('AllowEditing', None)

    @property
    def root_site_url(self):
        """

        :rtype: str or None
        """
        return self.properties.get('RootSiteUrl', None)

    @property
    def sites(self):
        """Gets a collection of sites."""
        return self.properties.get('sites',
                                   SitePropertiesCollection(self.context, ResourcePath("sites", self.resource_path)))

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.TenantAdministration.Tenant"
