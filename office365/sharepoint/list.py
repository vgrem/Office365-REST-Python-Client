from office365.sharepoint.content_type_collection import ContentTypeCollection
from office365.sharepoint.folder import Folder
from office365.sharepoint.listitem import ListItem
from office365.sharepoint.securable_object import SecurableObject
from office365.sharepoint.view import View
from office365.sharepoint.view_collection import ViewCollection
from office365.runtime.action_type import ActionType
from office365.runtime.client_query import ClientQuery
from office365.runtime.resource_path_entry import ResourcePathEntry
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.sharepoint.listItem_collection import ListItemCollection


class List(SecurableObject):
    """List client object"""

    def get_items(self):
        """Returns a collection of items from the list based on the specified query."""
        items = ListItemCollection(self.context, ResourcePathEntry(self.context, self.resource_path, "items"))
        return items

    def add_item(self, list_item_creation_information):
        """The recommended way to add a list item is to send a POST request to the ListItemCollection resource endpoint,
         as shown in ListItemCollection request examples."""
        item = ListItem(self.context, None, list_item_creation_information)
        qry = ClientQuery(self.url + "/items", ActionType.CreateEntry, item.convert_to_payload())
        self.context.add_query(qry, item)
        return item

    def get_item_by_id(self, item_id):
        """Returns the list item with the specified list item identifier."""
        list_item = ListItem(self.context,
                             ClientQuery.service_operation_query(self, ActionType.GetMethod, "getitembyid", [item_id]))
        return list_item

    def get_view(self, view_id):
        """Returns the list view with the specified view identifier."""
        view = View(self.context, ResourcePathServiceOperation(self.context,
                                                               self.resource_path,
                                                               "getview",
                                                               [view_id]))
        return view

    def update(self):
        qry = ClientQuery.update_entry_query(self)
        self.context.add_query(qry)

    def delete_object(self):
        """Deletes the list."""
        qry = ClientQuery.delete_entry_query(self)
        self.context.add_query(qry)
        # self.removeFromParentCollection()

    @property
    def root_folder(self):
        """Get a root folder"""
        if self.is_property_available('RootFolder'):
            return self.properties["RootFolder"]
        else:
            return Folder(self.context, ResourcePathEntry(self.context, self.resource_path, "RootFolder"))

    @property
    def views(self):
        """Gets a value that specifies the collection of all public views on the list and personal views
        of the current user on the list."""
        if self.is_property_available('Views'):
            return self.properties['Views']
        else:
            return ViewCollection(self.context, ResourcePathEntry(self.context, self.resource_path, "views"))

    @property
    def content_types(self):
        """Gets the content types that are associated with the list."""
        if self.is_property_available('ContentTypes'):
            return self.properties['ContentTypes']
        else:
            return ContentTypeCollection(self.context,
                                         ResourcePathEntry(self.context, self.resource_path, "contenttypes"))
