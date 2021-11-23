from office365.base_item import BaseItem
from office365.entity_collection import EntityCollection
from office365.onedrive.analytics.item_activity_stat import ItemActivityStat
from office365.onedrive.columns.column_definition import ColumnDefinition
from office365.onedrive.contenttypes.content_type import ContentType
from office365.onedrive.drives.drive import Drive
from office365.onedrive.analytics.item_analytics import ItemAnalytics
from office365.onedrive.lists.list_collection import ListCollection
from office365.onedrive.listitems.list_item import ListItem
from office365.onedrive.permissions.permission import Permission
from office365.onedrive.sharepoint_ids import SharePointIds
from office365.onedrive.sites.site_collection import SiteCollection
from office365.onenote.onenote import Onenote
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath


class Site(BaseItem):
    """The site resource provides metadata and relationships for a SharePoint site. """

    def get_by_path(self, path):
        """
        Retrieve properties and relationships for a site resource. A site resource represents a team site in SharePoint.

            In addition to retrieving a site by ID you can retrieve a site based on server-relative URL path.

            Site collection hostname (contoso.sharepoint.com)
            Site path, relative to server hostname.
            There is also a reserved site identifier, root, which always references the root site for a given target,
            as follows:

            /sites/root: The tenant root site.
            /groups/{group-id}/sites/root: The group's team site.

        :type path: str
        """
        return_site = Site(self.context)
        qry = ServiceOperationQuery(self, "GetByPath", [path], None, None, return_site)
        self.context.add_query(qry)
        return return_site

    def get_activities_by_interval(self, start_dt=None, end_dt=None, interval=None):
        """
        Get a collection of itemActivityStats resources for the activities that took place on this resource
        within the specified time interval.

        :param datetime.datetime start_dt: The start time over which to aggregate activities.
        :param datetime.datetime end_dt: The end time over which to aggregate activities.
        :param str interval: The aggregation interval.
        """
        params = {
            "startDateTime": start_dt.strftime('%m-%d-%Y') if start_dt else None,
            "endDateTime": end_dt.strftime('%m-%d-%Y') if end_dt else None,
            "interval": interval
        }
        return_type = EntityCollection(self.context, ItemActivityStat)
        qry = ServiceOperationQuery(self, "getActivitiesByInterval", params, None, None, return_type)
        self.context.add_query(qry)

        def _construct_request(request):
            request.method = HttpMethod.Get

        self.context.before_execute(_construct_request)
        return return_type

    @property
    def site_collection(self):
        """Provides details about the site's site collection. Available only on the root site."""
        return self.properties.get("siteCollection", SiteCollection())

    @property
    def sharepoint_ids(self):
        """Returns identifiers useful for SharePoint REST compatibility."""
        return self.properties.get('sharepointIds', SharePointIds())

    @property
    def items(self):
        """Used to address any item contained in this site. This collection cannot be enumerated."""
        return self.get_property('items',
                                 EntityCollection(self.context, ListItem, ResourcePath("items", self.resource_path)))

    @property
    def columns(self):
        """The collection of columns under this site."""
        return self.properties.get('columns',
                                   EntityCollection(self.context, ColumnDefinition,
                                                    ResourcePath("columns", self.resource_path)))

    @property
    def content_types(self):
        """The collection of content types under this site."""
        return self.properties.get('contentTypes',
                                   EntityCollection(self.context, ContentType,
                                                    ResourcePath("contentTypes", self.resource_path)))

    @property
    def lists(self):
        """The collection of lists under this site."""
        return self.properties.get('lists',
                                   ListCollection(self.context, ResourcePath("lists", self.resource_path)))

    @property
    def permissions(self):
        """The collection of lists under this site."""
        return self.properties.get('permissions',
                                   EntityCollection(self.context, Permission,
                                                    ResourcePath("permissions", self.resource_path)))

    @property
    def drive(self):
        """The default drive (document library) for this site."""
        return self.properties.get('drive',
                                   Drive(self.context, ResourcePath("drive", self.resource_path)))

    @property
    def drives(self):
        """The collection of drives under this site."""
        return self.properties.get('drives',
                                   EntityCollection(self.context, Drive, ResourcePath("drives", self.resource_path)))

    @property
    def sites(self):
        """The collection of sites under this site."""
        return self.properties.get('sites',
                                   EntityCollection(self.context, Site, ResourcePath("sites", self.resource_path)))

    @property
    def analytics(self):
        """Analytics about the view activities that took place on this site."""
        return self.properties.get('analytics',
                                   ItemAnalytics(self.context, ResourcePath("analytics", self.resource_path)))

    @property
    def onenote(self):
        """Represents the Onenote services available to a site."""
        return self.properties.get('onenote',
                                   Onenote(self.context, ResourcePath("onenote", self.resource_path)))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "contentTypes": self.content_types
            }
            default_value = property_mapping.get(name, None)
        return super(Site, self).get_property(name, default_value)

    def set_property(self, name, value, persist_changes=True):
        super(Site, self).set_property(name, value, persist_changes)
        if name == "id" and self.resource_path.name == "root":
            self._resource_path = ResourcePath(value, self.resource_path.parent)
        return self
