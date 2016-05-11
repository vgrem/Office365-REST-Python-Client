from client.client_object import ClientObject
from client.content_type_collection import ContentTypeCollection
from client.folder import Folder
from client.listitem import ListItem
from client.listItem_collection import ListItemCollection
from client.view import View
from client.view_collection import ViewCollection
from client.runtime.client_query import ClientQuery


class List(ClientObject):
    """List client object"""

    def get_items(self):
        """Returns a collection of items from the list based on the specified query."""
        items = ListItemCollection(self.context, "items", self.resource_path)
        return items

    def add_item(self, list_item_creation_information):
        """The recommended way to add a list item is to send a POST request to the ListItemCollection resource endpoint,
         as shown in ListItemCollection request examples."""
        item = ListItem(self.context)
        qry = ClientQuery.create_create_query(self.url + "/items", list_item_creation_information)
        self.context.add_query(qry, item)
        return item

    def get_item_by_id(self, item_id):
        """Returns the list item with the specified list item identifier."""
        list_item = ListItem(self.context, "getitembyid('{0}')".format(item_id), self.resource_path)
        return list_item

    def get_view(self, view_id):
        """Returns the list view with the specified view identifier."""
        view = View(self.context, "getview('{0}')".format(view_id), self.resource_path)
        return view

    def update(self, list_updation_information):
        qry = ClientQuery.create_update_query(self, list_updation_information)
        self.context.add_query(qry)

    def delete_object(self):
        """Deletes the list."""
        qry = ClientQuery.create_delete_query(self)
        self.context.add_query(qry)
        # self.removeFromParentCollection()

    @property
    def root_folder(self):
        """Get a root folder"""
        if self.is_property_available('RootFolder'):
            return self.properties["RootFolder"]
        else:
            return Folder(self.context, "rootfolder", self.resource_path)

    @property
    def views(self):
        """Gets a value that specifies the collection of all public views on the list and personal views
        of the current user on the list."""
        if self.is_property_available('Views'):
            return self.properties['Views']
        else:
            return ViewCollection(self.context, "views", self.resource_path)

    @property
    def content_types(self):
        """Gets the content types that are associated with the list."""
        if self.is_property_available('ContentTypes'):
            return self.properties['ContentTypes']
        else:
            return ContentTypeCollection(self.context, "contenttypes", self.resource_path)
