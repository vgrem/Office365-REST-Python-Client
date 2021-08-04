from office365.base_item import BaseItem
from office365.entity_collection import EntityCollection
from office365.onedrive.columnDefinition import ColumnDefinition
from office365.onedrive.contentType import ContentType
from office365.onedrive.drive import Drive
from office365.onedrive.driveCollection import DriveCollection
from office365.onedrive.itemAnalytics import ItemAnalytics
from office365.onedrive.listCollection import ListCollection
from office365.onedrive.listItemCollection import ListItemCollection
from office365.onedrive.permission import Permission
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.resource_path import ResourcePath


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

    @property
    def items(self):
        """Used to address any item contained in this site. This collection cannot be enumerated."""
        return self.properties.get('items',
                                   ListItemCollection(self.context, ResourcePath("items", self.resource_path)))

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
                                   DriveCollection(self.context, ResourcePath("drives", self.resource_path)))

    @property
    def sharepoint_ids(self):
        """Returns identifiers useful for SharePoint REST compatibility."""
        return self.properties.get('sharepointIds', None)

    @property
    def sites(self):
        """The collection of sites under this site."""
        from office365.onedrive.siteCollection import SiteCollection
        return self.properties.get('sites',
                                   SiteCollection(self.context, ResourcePath("sites", self.resource_path)))

    @property
    def analytics(self):
        """Analytics about the view activities that took place on this site."""
        return self.properties.get('analytics',
                                   ItemAnalytics(self.context, ResourcePath("analytics", self.resource_path)))

    def set_property(self, name, value, persist_changes=True):
        super(Site, self).set_property(name, value, persist_changes)
        if name == "id" and self._resource_path.segment == "root":
            self._resource_path = ResourcePath(value, self._resource_path.parent)
        return self
