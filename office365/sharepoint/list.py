from office365.runtime.client_query import UpdateEntityQuery, DeleteEntityQuery, ServiceOperationQuery
from office365.runtime.resource_path import ResourcePath
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.sharepoint.content_type_collection import ContentTypeCollection
from office365.sharepoint.field_collection import FieldCollection
from office365.sharepoint.folder import Folder
from office365.sharepoint.listitem import ListItem
from office365.sharepoint.listItem_collection import ListItemCollection
from office365.sharepoint.securable_object import SecurableObject
from office365.sharepoint.view import View
from office365.sharepoint.view_collection import ViewCollection


class List(SecurableObject):
    """List client object"""

    def __init__(self, context, resource_path=None):
        super(List, self).__init__(context, resource_path)
        self._items = None

    def get_items(self, caml_query=None):
        """Returns a collection of items from the list based on the specified query."""
        self._items = ListItemCollection(self.context, ResourcePath("items", self.resourcePath))
        if caml_query:
            qry = ServiceOperationQuery(self, "GetItems", None, caml_query, "query", self._items)
            self.context.add_query(qry)
        return self._items

    def add_item(self, list_item_creation_information):
        """The recommended way to add a list item is to send a POST request to the ListItemCollection resource endpoint,
         as shown in ListItemCollection request examples."""
        item = ListItem(self.context, None, list_item_creation_information)
        if self._items is None:
            self._items = ListItemCollection(self.context, ResourcePath("items", self.resourcePath))
        self._items.add_child(item)
        qry = ServiceOperationQuery(self, "items", None, item, None, item)
        self.context.add_query(qry)
        return item

    def get_item_by_id(self, item_id):
        """Returns the list item with the specified list item identifier."""
        return ListItem(self.context,
                        ResourcePathServiceOperation("getitembyid", [item_id], self.resourcePath))

    def get_view(self, view_id):
        """Returns the list view with the specified view identifier."""
        view = View(self.context, ResourcePathServiceOperation("getview", [view_id], self.resourcePath))
        return view

    def update(self):
        qry = UpdateEntityQuery(self)
        self.context.add_query(qry)

    def delete_object(self):
        """Deletes the list."""
        qry = DeleteEntityQuery(self)
        self.context.add_query(qry)
        self.remove_from_parent_collection()

    @property
    def rootFolder(self):
        """Get a root folder"""
        if self.is_property_available('RootFolder'):
            return self.properties["RootFolder"]
        else:
            return Folder(self.context, ResourcePath("RootFolder", self.resourcePath))

    @property
    def fields(self):
        """Gets a value that specifies the collection of all fields in the list."""
        if self.is_property_available('Fields'):
            return self.properties['Fields']
        else:
            return FieldCollection(self.context, ResourcePath("Fields", self.resourcePath))

    @property
    def views(self):
        """Gets a value that specifies the collection of all public views on the list and personal views
        of the current user on the list."""
        if self.is_property_available('Views'):
            return self.properties['Views']
        else:
            return ViewCollection(self.context, ResourcePath("views", self.resourcePath))

    @property
    def contentTypes(self):
        """Gets the content types that are associated with the list."""
        if self.is_property_available('ContentTypes'):
            return self.properties['ContentTypes']
        else:
            return ContentTypeCollection(self.context,
                                         ResourcePath("contenttypes", self.resourcePath))

    def set_property(self, name, value, persist_changes=True):
        super(List, self).set_property(name, value, persist_changes)
        # fallback: create a new resource path
        if self._resource_path is None:
            if name == "Id":
                self._resource_path = ResourcePathServiceOperation(
                    "GetById", [value], self._parent_collection.resourcePath)
            elif name == "Title":
                self._resource_path = ResourcePathServiceOperation(
                    "GetByTitle", [value], self._parent_collection.resourcePath)
