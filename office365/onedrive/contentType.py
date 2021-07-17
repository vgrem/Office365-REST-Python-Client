from office365.base_item import BaseItem
from office365.entity_collection import EntityCollection
from office365.onedrive.columnLink import ColumnLink
from office365.runtime.resource_path import ResourcePath


class ContentType(BaseItem):
    """The contentType resource represents a content type in SharePoint. Content types allow you to define a set of
    columns that must be present on every listItem in a list. """

    @property
    def name(self):
        return self.properties.get('name', None)

    @property
    def parent_id(self):
        return self.properties.get('parentId', None)

    @property
    def read_only(self):
        return self.properties.get('readOnly', None)

    @property
    def column_links(self):
        return self.properties.get('columnLinks',
                                   EntityCollection(self.context,
                                                    ColumnLink,
                                                    ResourcePath("columnLinks", self.resource_path)))
