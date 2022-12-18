from office365.base_item import BaseItem
from office365.entity_collection import EntityCollection
from office365.onedrive.columns.definition_collection import ColumnDefinitionCollection
from office365.onedrive.contenttypes.collection import ContentTypeCollection
from office365.onedrive.listitems.list_item import ListItem
from office365.onedrive.lists.info import ListInfo
from office365.onedrive.sharepoint_ids import SharePointIds
from office365.runtime.paths.resource_path import ResourcePath
from office365.subscriptions.subscription import Subscription


class List(BaseItem):
    """The list resource represents a list in a site. This resource contains the top level properties of the list,
    including template and field definitions. """

    @property
    def display_name(self):
        """
        The displayable title of the list.

        :rtype: str or None
        """
        return self.properties.get("displayName", None)

    @property
    def list(self):
        """Provides additional details about the list."""
        return self.properties.get('list', ListInfo())

    @property
    def sharepoint_ids(self):
        """Returns identifiers useful for SharePoint REST compatibility."""
        return self.properties.get('sharepointIds', SharePointIds())

    @property
    def drive(self):
        """Only present on document libraries. Allows access to the list as a drive resource with driveItems."""
        from office365.onedrive.drives.drive import Drive
        return self.properties.get('drive',
                                   Drive(self.context, ResourcePath("drive", self.resource_path)))

    @property
    def columns(self):
        """The collection of columns under this site."""
        return self.properties.get('columns',
                                   ColumnDefinitionCollection(self.context,
                                                              ResourcePath("columns", self.resource_path), self))

    @property
    def content_types(self):
        """The collection of content types under this site."""
        return self.properties.get('contentTypes',
                                   ContentTypeCollection(self.context,
                                                         ResourcePath("contentTypes", self.resource_path)))

    @property
    def items(self):
        """All items contained in the list."""
        return self.properties.get('items',
                                   EntityCollection(self.context, ListItem, ResourcePath("items", self.resource_path)))

    @property
    def subscriptions(self):
        """The set of subscriptions on the list."""
        return self.properties.get('subscriptions',
                                   EntityCollection(self.context, Subscription,
                                                    ResourcePath("subscriptions", self.resource_path)))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "contentTypes": self.content_types
            }
            default_value = property_mapping.get(name, None)
        return super(List, self).get_property(name, default_value)
