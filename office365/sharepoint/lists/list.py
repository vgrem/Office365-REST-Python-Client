from office365.runtime.client_query import DeleteEntityQuery
from office365.runtime.client_result import ClientResult
from office365.runtime.resource_path import ResourcePath
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.runtime.queries.serviceOperationQuery import ServiceOperationQuery
from office365.sharepoint.caml.camlQuery import CamlQuery
from office365.sharepoint.contenttypes.content_type_collection import ContentTypeCollection
from office365.sharepoint.fields.field_collection import FieldCollection
from office365.sharepoint.folders.folder import Folder
from office365.sharepoint.listitems.listitem import ListItem
from office365.sharepoint.listitems.listItem_collection import ListItemCollection
from office365.sharepoint.permissions.securable_object import SecurableObject
from office365.sharepoint.views.view import View
from office365.sharepoint.views.view_collection import ViewCollection


class List(SecurableObject):
    """List client object"""

    def __init__(self, context, resource_path=None):
        super(List, self).__init__(context, resource_path)

    def get_web_dav_url(self, source_url):
        result = ClientResult(None)
        qry = ServiceOperationQuery(self, "getWebDavUrl", [source_url], None, None, result)
        self.context.add_query(qry)
        return result

    def get_items(self, caml_query=None):
        """Returns a collection of items from the list based on the specified query.
        :type caml_query: CamlQuery
        """
        if not caml_query:
            caml_query = CamlQuery.create_all_items_query()
        items = ListItemCollection(self.context, ResourcePath("items", self.resource_path))
        qry = ServiceOperationQuery(self, "GetItems", None, caml_query, "query", items)
        self.context.add_query(qry)
        return items

    def add_item(self, list_item_creation_information):
        """The recommended way to add a list item is to send a POST request to the ListItemCollection resource endpoint,
         as shown in ListItemCollection request examples.
         :type list_item_creation_information: ListItemCreationInformation or dict"""
        item = ListItem(self.context)
        for k, v in list_item_creation_information.items():
            item.set_property(k, v, True)
        self.items.add_child(item)
        item.ensure_type_name(self)
        qry = ServiceOperationQuery(self, "items", None, item, None, item)
        self.context.add_query(qry)
        return item

    def get_item_by_id(self, item_id):
        """Returns the list item with the specified list item identifier.
        :type item_id: int
        """
        return ListItem(self.context,
                        ResourcePathServiceOperation("getItemById", [item_id], self.resource_path))

    def get_view(self, view_id):
        """Returns the list view with the specified view identifier.
        :type view_id: str
        """
        view = View(self.context, ResourcePathServiceOperation("getView", [view_id], self.resource_path), self)
        return view

    def delete_object(self):
        """Deletes the list."""
        qry = DeleteEntityQuery(self)
        self.context.add_query(qry)
        self.remove_from_parent_collection()

    @property
    def items(self):
        """Get list items"""
        if self.is_property_available('Items'):
            return self.properties["Items"]
        else:
            return ListItemCollection(self.context, ResourcePath("items", self.resource_path))

    @property
    def rootFolder(self):
        """Get a root folder"""
        if self.is_property_available('RootFolder'):
            return self.properties["RootFolder"]
        else:
            return Folder(self.context, ResourcePath("RootFolder", self.resource_path))

    @property
    def fields(self):
        """Gets a value that specifies the collection of all fields in the list."""
        if self.is_property_available('Fields'):
            return self.properties['Fields']
        else:
            return FieldCollection(self.context, ResourcePath("Fields", self.resource_path))

    @property
    def views(self):
        """Gets a value that specifies the collection of all public views on the list and personal views
        of the current user on the list."""
        if self.is_property_available('Views'):
            return self.properties['Views']
        else:
            return ViewCollection(self.context, ResourcePath("views", self.resource_path), self)

    @property
    def defaultView(self):
        """Gets or sets a value that specifies whether the list view is the default list view."""
        if self.is_property_available('DefaultView'):
            return self.properties['DefaultView']
        else:
            return View(self.context, ResourcePath("DefaultView", self.resource_path), self)

    @property
    def contentTypes(self):
        """Gets the content types that are associated with the list."""
        if self.is_property_available('ContentTypes'):
            return self.properties['ContentTypes']
        else:
            return ContentTypeCollection(self.context,
                                         ResourcePath("contenttypes", self.resource_path))

    def set_property(self, name, value, persist_changes=True):
        super(List, self).set_property(name, value, persist_changes)
        # fallback: create a new resource path
        if self._resource_path is None:
            if name == "Id":
                self._resource_path = ResourcePathServiceOperation(
                    "GetById", [value], self._parent_collection.resource_path)
            elif name == "Title":
                self._resource_path = ResourcePathServiceOperation(
                    "GetByTitle", [value], self._parent_collection.resource_path)
