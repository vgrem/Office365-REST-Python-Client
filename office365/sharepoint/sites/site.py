from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.audit.audit import Audit
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.changes.collection import ChangeCollection
from office365.sharepoint.changes.token import ChangeToken
from office365.sharepoint.eventreceivers.definition_collection import EventReceiverDefinitionCollection
from office365.sharepoint.features.collection import FeatureCollection
from office365.sharepoint.lists.list import List
from office365.sharepoint.portal.site_icon_manager import SiteIconManager
from office365.sharepoint.principal.user import User
from office365.sharepoint.recyclebin.item_collection import RecycleBinItemCollection
from office365.sharepoint.sitehealth.summary import SiteHealthSummary
from office365.sharepoint.sites.sph_site import SPHSite
from office365.sharepoint.sites.usage_info import UsageInfo
from office365.sharepoint.usercustomactions.collection import UserCustomActionCollection
from office365.sharepoint.webs.web import Web
from office365.sharepoint.webs.template_collection import WebTemplateCollection
from office365.sharepoint.types.resource_path import ResourcePath as SPResPath


class Site(BaseEntity):
    """Represents a collection of sites in a Web application, including a top-level website and all its sub sites."""

    def __init__(self, context, resource_path=None):
        super(Site, self).__init__(context, ResourcePath("Site", resource_path))

    def delete_object(self):
        """Deletes a site"""
        def _site_resolved():
            self.context.group_site_manager.delete(self.url)
        self.ensure_property("Url", _site_resolved)
        return self

    @staticmethod
    def from_url(url):
        """
        Initiates and returns a site instance

        :type url: str
        """
        from office365.sharepoint.client_context import ClientContext
        return ClientContext(url).site

    def get_site_logo(self):
        """
        Downloads a site logo
        """
        return_type = ClientResult(self.context)

        def _site_loaded():
            site_manager = SiteIconManager(self.context)
            site_manager.get_site_logo(self.url, return_type=return_type)

        self.ensure_property("Url", _site_loaded)
        return return_type

    def set_site_logo(self, relative_logo_url):
        """Uploads a site logo

        :param str relative_logo_url:
        """
        site_manager = SiteIconManager(self.context)
        site_manager.set_site_logo(relative_logo_url=relative_logo_url)
        return self

    def is_valid_home_site(self):
        """
        Determines whether a site is landing site for your intranet.
        """
        return_type = ClientResult(self.context)

        def _site_loaded():
            SPHSite.is_valid_home_site(self.context, self.url, return_type)

        self.ensure_property("Url", _site_loaded)
        return return_type

    def set_as_home_site(self):
        """
        Sets a site as a landing site for your intranet.
        """
        result = ClientResult(self.context)

        def _site_loaded():
            self.result = SPHSite.set_as_home_site(self.context, self.url, result)

        self.ensure_property("Url", _site_loaded)
        return result

    def get_changes(self, query):
        """Returns the collection of all changes from the change log that have occurred within the scope of the site,
        based on the specified query.

        :param office365.sharepoint.changes.query.ChangeQuery query: Specifies which changes to return
        """
        changes = ChangeCollection(self.context)
        qry = ServiceOperationQuery(self, "getChanges", None, query, "query", changes)
        self.context.add_query(qry)
        return changes

    def get_recycle_bin_items(self, row_limit=100, is_ascending=True):
        """
        Returns a collection of recycle bin items based on the specified query.

        :param int row_limit:
        :param bool is_ascending:
        """
        result = RecycleBinItemCollection(self.context)
        payload = {
            "rowLimit": row_limit,
            "isAscending": is_ascending
        }
        qry = ServiceOperationQuery(self, "GetRecycleBinItems", None, payload, None, result)
        self.context.add_query(qry)
        return result

    def get_web_templates(self, lcid=1033, override_compat_level=0):
        """
        Returns the collection of site definitions that are available for creating
            Web sites within the site collection.<99>

        :param int lcid: A 32-bit unsigned integer that specifies the language of the site definitions that are
            returned from the site collection.
        :param int override_compat_level: Specifies the compatibility level of the site (2)
            to return from the site collection. If this value is 0, the compatibility level of the site (2) is used.
        :return:
        """
        params = {
            "LCID": lcid,
            "overrideCompatLevel": override_compat_level
        }
        return_type = WebTemplateCollection(self.context,
                                            ServiceOperationPath("GetWebTemplates", params, self.resource_path))

        qry = ServiceOperationQuery(self, "GetWebTemplates", params, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def join_hub_site(self, hub_site_id, approval_token=None, approval_correlation_id=None):
        """
        Associates a site with an existing hub site.

        :param str hub_site_id: ID of the hub site to join.
        :param str approval_token:
        :param str approval_correlation_id:
        """
        payload = {
            "hubSiteId": hub_site_id,
            "approvalToken": approval_token,
            "approvalCorrelationId": approval_correlation_id
        }
        qry = ServiceOperationQuery(self, "JoinHubSite", None, payload)
        self.context.add_query(qry)
        return self

    @staticmethod
    def get_url_by_id(context, site_id, stop_redirect=False):
        """Gets Site Url By Id

        :type context: office365.sharepoint.client_context.ClientContext
        :type site_id: str
        :type stop_redirect: bool
        """
        result = ClientResult(context)
        payload = {
            "id": site_id,
            "stopRedirect": stop_redirect
        }
        qry = ServiceOperationQuery(context.site, "GetUrlById", None, payload, None, result)
        qry.static = True
        context.add_query(qry)
        return result

    @staticmethod
    def get_url_by_id_for_web(context, site_id, stop_redirect, web_id):
        """Gets Site Url By Id

        :type context: office365.sharepoint.client_context.ClientContext
        :type site_id: str
        :type stop_redirect: bool
        :type web_id: str
        """
        result = ClientResult(context)
        payload = {
            "id": site_id,
            "stopRedirect": stop_redirect,
            "webId": web_id
        }
        qry = ServiceOperationQuery(context.site, "GetUrlById", None, payload, None, result)
        qry.static = True
        context.add_query(qry)
        return result

    @staticmethod
    def exists(context, url):
        """Determine whether site exists

        :type context: office365.sharepoint.client_context.ClientContext
        :type url: str
        """
        result = ClientResult(context)
        payload = {
            "url": url
        }
        qry = ServiceOperationQuery(context.site, "Exists", None, payload, None, result)
        qry.static = True
        context.add_query(qry)
        return result

    def get_catalog(self, type_catalog):
        """
        Specifies the list template gallery, site template gallery, Web Part gallery, master page gallery,
        or other galleries from the site collection, including custom galleries that are defined by users.

        :type type_catalog: int
        """
        return List(self.context, ServiceOperationPath("getCatalog", [type_catalog], self.resource_path))

    def open_web(self, str_url):
        """Returns the specified Web site from the site collection.

        :param str str_url: A string that contains either the server-relative or site-relative URL of the
        Web site or of an object within the Web site. A server-relative URL begins with a forward slash ("/"),
        while a site-relative URL does not begin with a forward slash.
        """
        return_type = Web(self.context)
        qry = ServiceOperationQuery(self, "OpenWeb", {"strUrl": str_url}, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def open_web_by_id(self, web_id):
        """Returns the specified Web site from the site collection.

        :param str web_id: An identifier of the Web site
        """
        return_type = Web(self.context)
        qry = ServiceOperationQuery(self, "OpenWebById", {"gWebId": web_id}, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def register_hub_site(self, create_info=None):
        """Registers an existing site as a hub site.

        :type create_info: HubSiteCreationInformation
        """
        qry = ServiceOperationQuery(self, "RegisterHubSite", None, create_info, "creationInformation", None)
        self.context.add_query(qry)
        return self

    def run_health_check(self, rule_id=None, repair=None, run_always=None):
        """
        Runs a health check as follows. (The health rules referenced below perform an implementation-dependent check
        on the health of a site collection.)

        :param str rule_id: Specifies the rule or rules to be run. If the value is an empty GUID, all rules are run,
             otherwise only the specified rule is run.
        :param bool repair: Specifies whether repairable rules are to be run in repair mode.
        :param bool run_always: Specifies whether the rules will be run as a result of this call or cached results
             from a previous run can be returned.
        """
        payload = {
            "ruleId": rule_id,
            "bRepair": repair,
            "bRunAlways": run_always
        }
        return_type = SiteHealthSummary(self.context)
        qry = ServiceOperationQuery(self, "RunHealthCheck", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def unregister_hub_site(self):
        """
        Disables the hub site feature on a site.
        """
        qry = ServiceOperationQuery(self, "UnRegisterHubSite")
        self.context.add_query(qry)
        return self

    @property
    def allow_designer(self):
        """
        Specifies whether a designer can be used on this site collection.
        See Microsoft.SharePoint.Client.Web.AllowDesignerForCurrentUser, which is the scalar property used
        to determine the behavior for the current user. The default, if not disabled on the Web application, is "true".

        :rtype: bool or None
        """
        return self.properties.get("AllowDesigner", None)

    @property
    def audit(self):
        """
        Enables auditing of how site collection is accessed, changed, and used.
        """
        return self.properties.get("Audit", Audit(self.context, ResourcePath("Audit", self.resource_path)))

    @property
    def can_upgrade(self):
        """
        Specifies whether this site collection is in an implementation-specific valid state for site collection upgrade,
         "true" if it is; otherwise, "false".

        :rtype: bool
        """
        return self.properties.get("CanUpgrade", None)

    @property
    def classification(self):
        """
        Gets the classification of this site.

        :rtype: str or None
        """
        return self.properties.get("Classification", None)

    @property
    def current_change_token(self):
        """Gets the current change token that is used in the change log for the site collection."""
        return self.properties.get("CurrentChangeToken", ChangeToken())

    @property
    def group_id(self):
        """
        :rtype: str or None
        """
        return self.properties.get("GroupId", None)

    @property
    def root_web(self):
        """Get root web"""
        return self.properties.get('RootWeb', Web(self.context, ResourcePath("RootWeb", self.resource_path)))

    @property
    def owner(self):
        """Gets or sets the owner of the site collection. (Read-only in sandboxed solutions.)"""
        return self.properties.get('Owner', User(self.context, ResourcePath("Owner", self.resource_path)))

    @property
    def read_only(self):
        """
        Gets a Boolean value that specifies whether the site collection is read-only,
        locked, and unavailable for write access.

        :rtype: bool
        """
        return self.properties.get("ReadOnly", None)

    @property
    def required_designer_version(self):
        """
        Specifies the required minimum version of the designer that can be used on this site collection.
        The default, if not disabled on the Web application, is "15.0.0.0".

        :rtype: str
        """
        return self.properties.get("RequiredDesignerVersion", None)

    @property
    def url(self):
        """
        Specifies the full URL of the site (2), including host name, port number and path.

        :rtype: str
        """
        return self.properties.get('Url', None)

    @property
    def server_relative_url(self):
        """
        Specifies the server-relative URL of the top-level site in the site collection.

        :rtype: str
        """
        return self.properties.get("ServerRelativeUrl", None)

    @property
    def share_by_email_enabled(self):
        """
        When true, users will be able to grant permissions to guests for resources within the site collection.

        :rtype: bool or none
        """
        return self.properties.get('ShareByEmailEnabled', None)

    @property
    def trim_audit_log(self):
        """
        When this flag is set for the site, the audit events are trimmed periodically.

        :rtype: bool or none
        """
        return self.properties.get('TrimAuditLog', None)

    @property
    def write_locked(self):
        """
        :rtype: bool or none
        """
        return self.properties.get('WriteLocked', None)

    @property
    def id(self):
        """
        Specifies the GUID that identifies the site collection.

        :rtype: str
        """
        return self.properties.get("Id", None)

    @property
    def hub_site_id(self):
        """
        :rtype: str
        """
        return self.properties.get("HubSiteId", None)

    @property
    def is_hub_site(self):
        """
        Returns whether the specified site is a hub site

        :rtype: bool
        """
        return self.properties.get("IsHubSite", None)

    @property
    def server_relative_path(self):
        """Gets the server-relative Path of the Site.

        :rtype: SPResPath or None
        """
        return self.properties.get("ServerRelativePath", SPResPath())

    @property
    def secondary_contact(self):
        """Gets or sets the secondary contact that is used for the site collection."""
        return self.properties.get('SecondaryContact', User(self.context,
                                                            ResourcePath("SecondaryContact", self.resource_path)))

    @property
    def recycle_bin(self):
        """Get recycle bin"""
        return self.properties.get('RecycleBin',
                                   RecycleBinItemCollection(self.context,
                                                            ResourcePath("RecycleBin", self.resource_path)))

    @property
    def features(self):
        """Get features"""
        return self.properties.get('Features',
                                   FeatureCollection(self.context,
                                                     ResourcePath("Features", self.resource_path), self))

    @property
    def event_receivers(self):
        """
        Provides event receivers for events that occur at the scope of the site collection.
        """
        return self.properties.get('EventReceivers',
                                   EventReceiverDefinitionCollection(self.context,
                                                                     ResourcePath("eventReceivers", self.resource_path),
                                                                     self))

    @property
    def usage_info(self):
        """Provides fields used to access information regarding site collection usage."""
        return self.properties.get("UsageInfo", UsageInfo())

    @property
    def user_custom_actions(self):
        """Gets the User Custom Actions that are associated with the site."""
        return self.properties.get('UserCustomActions',
                                   UserCustomActionCollection(self.context,
                                                              ResourcePath("UserCustomActions", self.resource_path)))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "CurrentChangeToken": self.current_change_token,
                "EventReceivers": self.event_receivers,
                "RecycleBin": self.recycle_bin,
                "RootWeb": self.root_web,
                "SecondaryContact": self.secondary_contact,
                "UsageInfo": self.usage_info,
                "UserCustomActions": self.user_custom_actions
            }
            default_value = property_mapping.get(name, None)
        return super(Site, self).get_property(name, default_value)

    def set_property(self, name, value, persist_changes=True):
        if name == "__siteUrl":
            super(Site, self).set_property("Url", value)
            self._context = self.context.clone(value)
        else:
            super(Site, self).set_property(name, value, persist_changes)
        return self
