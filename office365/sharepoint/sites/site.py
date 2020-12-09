from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.resource_path import ResourcePath
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.changes.change_collection import ChangeCollection
from office365.sharepoint.features.feature_collection import FeatureCollection
from office365.sharepoint.lists.list import List
from office365.sharepoint.principal.user import User
from office365.sharepoint.recyclebin.recycleBinItemCollection import RecycleBinItemCollection
from office365.sharepoint.sites.sph_site import SPHSite
from office365.sharepoint.webs.web import Web
from office365.sharepoint.webs.web_template_collection import WebTemplateCollection


class Site(BaseEntity):
    """Represents a collection of sites in a Web application, including a top-level website and all its sub sites."""

    def __init__(self, context):
        super(Site, self).__init__(context, ResourcePath("Site", None))

    def is_valid_home_site(self):
        result = ClientResult(None)

        def _site_loaded():
            SPHSite.is_valid_home_site(self.context, self.url, result)

        self.ensure_property("Url", _site_loaded)
        return result

    def set_as_home_site(self):
        result = ClientResult(None)

        def _site_loaded():
            self.result = SPHSite.set_as_home_site(self.context, self.url, result)

        self.ensure_property("Url", _site_loaded)
        return result

    def get_changes(self, query):
        """Returns the collection of all changes from the change log that have occurred within the scope of the site,
        based on the specified query.

        :param office365.sharepoint.changes.change_query.ChangeQuery query: Specifies which changes to return
        """
        changes = ChangeCollection(self.context)
        qry = ServiceOperationQuery(self, "getChanges", None, query, "query", changes)
        self.context.add_query(qry)
        return changes

    def get_recycle_bin_items(self, pagingInfo=None, rowLimit=100, isAscending=True, orderBy=None, itemState=None):
        result = RecycleBinItemCollection(self.context)
        payload = {
            "rowLimit": rowLimit,
            "isAscending": isAscending
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
                                            ResourcePathServiceOperation("GetWebTemplates", params, self.resource_path))

        qry = ServiceOperationQuery(self, "GetWebTemplates", params, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def join_hub_site(self, hubSiteId, approvalToken, approvalCorrelationId):
        params = {
            "hubSiteId": hubSiteId,
            "approvalToken": approvalToken,
            "approvalCorrelationId": approvalCorrelationId
        }
        return_type = WebTemplateCollection(self.context,
                                            ResourcePathServiceOperation("GetWebTemplates", params, self.resource_path))

        qry = ServiceOperationQuery(self, "JoinHubSite", params, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    @staticmethod
    def get_url_by_id(context, site_id, stop_redirect=False):
        """Gets Site Url By Id
        :type context: office365.sharepoint.client_context.ClientContext
        :type site_id: str
        :type stop_redirect: bool
        """
        result = ClientResult(str)
        payload = {
            "id": site_id,
            "stopRedirect": stop_redirect
        }
        qry = ServiceOperationQuery(context.site, "GetUrlById", None, payload, None, result)
        qry.static = True
        context.add_query(qry)
        return result

    @staticmethod
    def get_url_by_id_for_web(context):
        pass

    @staticmethod
    def exists(context, url):
        """Determine whether site exists
        :type context: office365.sharepoint.client_context.ClientContext
        :type url: str
        """
        result = ClientResult(bool)
        payload = {
            "url": url
        }
        qry = ServiceOperationQuery(context.site, "Exists", None, payload, None, result)
        qry.static = True
        context.add_query(qry)
        return result

    def get_catalog(self, type_catalog):
        """Specifies the list template gallery, site template gallery, Web Part gallery, master page gallery,
        or other galleries from the site collection, including custom galleries that are defined by users.
        :type type_catalog: int"""
        return List(self.context, ResourcePathServiceOperation("getCatalog", [type_catalog], self.resource_path))

    @property
    def rootWeb(self):
        """Get root web"""
        if self.is_property_available('RootWeb'):
            return self.properties['RootWeb']
        else:
            return Web(self.context, ResourcePath("RootWeb", self.resource_path))

    @property
    def owner(self):
        """Gets or sets the owner of the site collection. (Read-only in sandboxed solutions.)"""
        if self.is_property_available('owner'):
            return self.properties['owner']
        else:
            return User(self.context, ResourcePath("owner", self.resource_path))

    @property
    def url(self):
        return self.properties.get('Url', None)

    @property
    def id(self):
        """
        :rtype: str
        """
        return self.properties.get("Id", None)

    @property
    def recycleBin(self):
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
