from office365.base_item import BaseItem
from office365.entity_collection import EntityCollection
from office365.onedrive.columns.column_link import ColumnLink
from office365.onedrive.listitems.item_reference import ItemReference
from office365.runtime.paths.resource_path import ResourcePath


class ContentType(BaseItem):
    """The contentType resource represents a content type in SharePoint. Content types allow you to define a set of
    columns that must be present on every listItem in a list. """

    @property
    def name(self):
        """
        The name of the content type.

        :rtype: str or None
        """
        return self.properties.get('name', None)

    @property
    def description(self):
        """
        The descriptive text for the item.

        :rtype: str or None
        """
        return self.properties.get('description', None)

    @property
    def parent_id(self):
        """The unique identifier of the content type.

        :rtype: str or None
        """
        return self.properties.get('parentId', None)

    @property
    def read_only(self):
        """
        If true, the content type cannot be modified unless this value is first set to false.

        :rtype: bool or None
        """
        return self.properties.get('readOnly', None)

    @property
    def inherited_from(self):
        """
        If this content type is inherited from another scope (like a site),
        provides a reference to the item where the content type is defined.
        """
        return self.properties.get("inheritedFrom", ItemReference())

    @property
    def column_links(self):
        """The collection of columns that are required by this content type"""
        return self.properties.get('columnLinks',
                                   EntityCollection(self.context,
                                                    ColumnLink, ResourcePath("columnLinks", self.resource_path)))
