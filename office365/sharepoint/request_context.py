from __future__ import annotations

from typing import TYPE_CHECKING

from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.lists.list import List
    from office365.sharepoint.request_context import RequestContext
    from office365.sharepoint.sites.site import Site
    from office365.sharepoint.webs.web import Web


class RequestContext(Entity):
    """
    Provides basic WSS context information: site, web, list, and list item.

    Use this class to return context information about such objects as the current Web application, site collection,
        site, list, or list item.
    """

    def get_remote_context(self) -> "RequestContext":
        """
        Returns the SP.RequestContext for the mounted folder.
        Returns null if this is not an attempt to render or act upon a mounted folder.
        """
        return_type = RequestContext(self.context)
        qry = ServiceOperationQuery(self, "GetRemoteContext", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def current(self) -> RequestContext:
        """Gets the Current property"""
        from office365.sharepoint.request_context import RequestContext

        return self.properties.get("Current", RequestContext(self.context, ResourcePath("Current", self.resource_path)))

    @property
    def list(self) -> List:
        """Gets the List property"""
        from office365.sharepoint.lists.list import List

        return self.properties.get("List", List(self.context, ResourcePath("List", self.resource_path)))

    @property
    def site(self) -> Site:
        """Gets the Site property"""
        from office365.sharepoint.sites.site import Site

        return self.properties.get("Site", Site(self.context, ResourcePath("Site", self.resource_path)))

    @property
    def web(self) -> Web:
        """Gets the Web property"""
        from office365.sharepoint.webs.web import Web

        return self.properties.get("Web", Web(self.context, ResourcePath("Web", self.resource_path)))
