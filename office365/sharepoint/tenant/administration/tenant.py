import time

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.gtp.request_options import ChatGptRequestOptions
from office365.sharepoint.listitems.collection import ListItemCollection
from office365.sharepoint.lists.render_data_parameters import RenderListDataParameters
from office365.sharepoint.lists.render_override_parameters import RenderListDataOverrideParameters
from office365.sharepoint.publishing.portal_health_status import PortalHealthStatus
from office365.sharepoint.sites.home_sites_details import HomeSitesDetails
from office365.sharepoint.sites.site import Site
from office365.sharepoint.tenant.administration.collaboration.insights_data import CollaborationInsightsData
from office365.sharepoint.tenant.administration.hubsites.properties import HubSiteProperties
from office365.sharepoint.tenant.administration.insights.onedrive_site_sharing import OneDriveSiteSharingInsights
from office365.sharepoint.tenant.administration.secondary_administrators_fields_data import \
    SecondaryAdministratorsFieldsData
from office365.sharepoint.tenant.administration.secondary_administrators_info import SecondaryAdministratorsInfo
from office365.sharepoint.tenant.administration.sites.administrators_info import SiteAdministratorsInfo
from office365.sharepoint.tenant.administration.sites.creation_properties import SiteCreationProperties
from office365.sharepoint.tenant.administration.sites.properties import SiteProperties
from office365.sharepoint.tenant.administration.sites.properties_collection import SitePropertiesCollection
from office365.sharepoint.tenant.administration.sites.properties_enumerable_filter import SitePropertiesEnumerableFilter
from office365.sharepoint.tenant.administration.siteinfo_for_site_picker import SiteInfoForSitePicker
from office365.sharepoint.tenant.administration.spo_operation import SpoOperation
from office365.sharepoint.tenant.administration.insights.top_files_sharing import TopFilesSharingInsights
from office365.sharepoint.tenant.administration.webs.templates.collection import SPOTenantWebTemplateCollection
from office365.sharepoint.tenant.settings import TenantSettings


class Tenant(BaseEntity):
    """Represents a SharePoint tenant."""

    def __init__(self, context):
        static_path = ResourcePath("Microsoft.Online.SharePoint.TenantAdministration.Tenant")
        super(Tenant, self).__init__(context, static_path)

    def get_corporate_catalog_site(self):
        """Retrieves Corporate Catalog Site"""
        settings = TenantSettings.current(self.context)
        return_type = Site(self.context)

        def _settings_loaded():
            return_type.set_property("__siteUrl", settings.corporate_catalog_url)
        settings.ensure_property("CorporateCatalogUrl", _settings_loaded)
        return return_type

    def get_chat_gpt_response(self):
        """"""
        return_type = ClientResult(self.context)
        payload = {"requestOptions": ChatGptRequestOptions()}
        qry = ServiceOperationQuery(self, "GetChatGptResponse", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def delete_policy_definition(self, item_id):
        """
        :param int item_id:
        """
        qry = ServiceOperationQuery(self, "DeletePolicyDefinition", None, {"itemId": item_id})
        self.context.add_query(qry)
        return self

    def delete_recent_admin_action_report(self, report_id):
        """
        :param int report_id:
        """
        qry = ServiceOperationQuery(self, "DeleteRecentAdminActionReport", None, {"reportId": report_id})
        self.context.add_query(qry)
        return self

    def get_spo_tenant_all_web_templates(self):
        return_type = SPOTenantWebTemplateCollection(self.context)
        qry = ServiceOperationQuery(self, "GetSPOTenantAllWebTemplates", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_onedrive_site_sharing_insights(self, query_mode):
        return_type = ClientResult(self.context, OneDriveSiteSharingInsights())
        payload = {"queryMode": query_mode}
        qry = ServiceOperationQuery(self, "GetOneDriveSiteSharingInsights", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_collaboration_insights_data(self):
        return_type = ClientResult(self.context, CollaborationInsightsData())
        qry = ServiceOperationQuery(self, "GetCollaborationInsightsData", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def render_recent_admin_actions(self):
        return_type = ClientResult(self.context)
        payload = {
            "parameters": RenderListDataParameters(),
            "overrideParameters": RenderListDataOverrideParameters()
        }
        qry = ServiceOperationQuery(self, "RenderRecentAdminActions", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_top_files_sharing_insights(self, query_mode):
        """
        :param int query_mode:
        """
        payload = {"queryMode": query_mode}
        return_type = BaseEntityCollection(self.context, TopFilesSharingInsights)
        qry = ServiceOperationQuery(self, "GetTopFilesSharingInsights", payload, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_site_thumbnail_logo(self, site_url):
        """
        :param str site_url:
        """
        payload = {"siteUrl": site_url}
        return_type = ClientResult(self.context, bytes())
        qry = ServiceOperationQuery(self, "GetSiteThumbnailLogo", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_home_site_url(self):
        """
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "GetSPHSiteUrl", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

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

    def remove_home_site(self, home_site_url):
        """
        Remove home site

        :param str home_site_url:
        """
        payload = {"homeSiteUrl": home_site_url}
        qry = ServiceOperationQuery(self, "RemoveHomeSite", None, payload)
        self.context.add_query(qry)
        return self

    def has_valid_education_license(self):
        """"""
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(self, "HasValidEducationLicense", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def export_to_csv(self, view_xml=None):
        """
        :param str view_xml:
        """
        return_type = ClientResult(self.context)
        payload = {
            "viewXml": view_xml
        }
        qry = ServiceOperationQuery(self, "ExportToCSV", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def render_policy_report(self):
        """"""
        return_type = ClientResult(self.context, bytes())
        payload = {
            "parameters": RenderListDataParameters(),
            "overrideParameters": RenderListDataOverrideParameters()
        }
        qry = ServiceOperationQuery(self, "RenderPolicyReport", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    @staticmethod
    def from_url(admin_site_url):
        """
        :type admin_site_url: str
        """
        from office365.sharepoint.client_context import ClientContext
        admin_client = ClientContext(admin_site_url)
        return Tenant(admin_client)

    def get_lock_state_by_id(self, site_id):
        """
        :param str site_id:
        """
        return self.sites.get_lock_state_by_id(site_id)

    def hub_sites(self, site_url):
        pass

    def check_tenant_intune_license(self):
        """
        Checks whether a tenant has the Intune license.
        """
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(self, "CheckTenantIntuneLicense", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def check_tenant_licenses(self, licenses):
        """
        Checks whether a tenant has the specified licenses.

        :param list[str] licenses: The list of licenses to check for.
        """
        return_type = ClientResult(self.context, bool())
        params = ClientValueCollection(str, licenses)
        qry = ServiceOperationQuery(self, "CheckTenantLicenses", None, params, "licenses", return_type)
        self.context.add_query(qry)
        return return_type

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

    def get_site_administrators(self, site_id, return_type=None):
        """
        Gets site collection administrators

        :type site_id: str
        :type return_type: ClientResult
        """
        if return_type is None:
            return_type = ClientResult(self.context, ClientValueCollection(SiteAdministratorsInfo))
        payload = {"siteId": site_id}
        qry = ServiceOperationQuery(self, "GetSiteAdministrators", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_site_secondary_administrators(self, site_id):
        """
        Gets site collection administrators

        :param str site_id: Site identifier
        """
        return_type = ClientResult(self.context, ClientValueCollection(SecondaryAdministratorsInfo))
        payload = {"secondaryAdministratorsFieldsData": SecondaryAdministratorsFieldsData(site_id)}
        qry = ServiceOperationQuery(self, "GetSiteSecondaryAdministrators", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def set_site_secondary_administrators(self, site_id, emails=None, names=None):
        """
        Sets site collection administrators

        :type names: list[str] or None
        :type emails: list[str]
        :type site_id: str
        """
        payload = {"secondaryAdministratorsFieldsData": SecondaryAdministratorsFieldsData(site_id, emails, names)}
        qry = ServiceOperationQuery(self, "SetSiteSecondaryAdministrators", None, payload, None, None)
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
        payload = {"siteCreationProperties": SiteCreationProperties(title=title, url=url, owner=owner)}
        qry = ServiceOperationQuery(self, "CreateSite", None, payload, None, return_type)
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
            resp.raise_for_status()
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
        return_type = SpoOperation(self.context)
        params = {"siteUrl": site_url}
        qry = ServiceOperationQuery(self, "removeSite", None, params, None, return_type)
        self.context.add_query(qry)
        return return_type

    def remove_deleted_site(self, site_url):
        """Permanently removes the specified deleted site from the recycle bin.

        :param str site_url: A string representing the URL of the site.
        """
        result = SpoOperation(self.context)
        qry = ServiceOperationQuery(self, "RemoveDeletedSite", [site_url], None, None, result)
        self.context.add_query(qry)
        return result

    def reorder_home_sites(self, home_sites_site_ids):
        """
        :param list[str] home_sites_site_ids:
        """
        payload = {
            "homeSitesSiteIds": home_sites_site_ids
        }
        return_type = ClientResult(self.context, ClientValueCollection(HomeSitesDetails))
        qry = ServiceOperationQuery(self, "ReorderHomeSites", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def restore_deleted_site(self, site_url):
        """Restores deleted site with the specified URL

        :param str site_url: A string representing the URL of the site.
        """
        return_type = SpoOperation(self.context)
        qry = ServiceOperationQuery(self, "RestoreDeletedSite", [site_url], None, None, return_type)
        self.context.add_query(qry)
        return return_type

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

    def get_site_properties_from_sharepoint_by_filters(self, _filter=None, start_index=None, include_detail=False):
        """

        :param bool include_detail:
        :param str start_index:
        :param str _filter:
        """
        return_type = SitePropertiesCollection(self.context)
        payload = {"speFilter": SitePropertiesEnumerableFilter(_filter, start_index, include_detail)}
        qry = ServiceOperationQuery(self, "getSitePropertiesFromSharePointByFilters", None, payload, None, return_type)
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

    def send_email(self, site_url):
        """
        :type site_url: str
        """
        return_type = ClientResult(self.context, bool())
        payload = {"siteUrl": site_url}
        qry = ServiceOperationQuery(self, "SendEmail", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def ai_builder_site_info_list(self):
        return self.properties.get("AIBuilderSiteInfoList", ClientValueCollection(SiteInfoForSitePicker))

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
    def default_content_center_site(self):
        return self.properties.get("DefaultContentCenterSite", SiteInfoForSitePicker())

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
