from office365.runtime.client_object import ClientObject
from office365.runtime.client_result import ClientResult
from office365.runtime.resource_path import ResourcePath
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.runtime.serviceOperationQuery import ServiceOperationQuery
from office365.sharepoint.list import List
from office365.sharepoint.user import User
from office365.sharepoint.web import Web


class Site(ClientObject):
    """Represents a collection of sites in a Web application, including a top-level website and all its subsites."""

    def __init__(self, context):
        super(Site, self).__init__(context, ResourcePath("Site", None))

    @staticmethod
    def exists(context, url):
        """Determine whether site exists
        :type context: ClientRuntimeContext
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
