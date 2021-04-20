from office365.runtime.client_result import ClientResult
from office365.runtime.queries.delete_entity_query import DeleteEntityQuery
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.resource_path import ResourcePath
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.contenttypes.content_type_id import ContentTypeId
from office365.sharepoint.listitems.caml.caml_query import CamlQuery
from office365.sharepoint.views.view_field_collection import ViewFieldCollection


class View(BaseEntity):
    """Specifies a list view."""

    def __init__(self, context, resource_path=None, parent_list=None):
        super(View, self).__init__(context, resource_path)
        self._parent_list = parent_list

    def get_property(self, name):
        if name == "ViewFields":
            return self.view_fields
        elif name == "DefaultView":
            return self.default_view
        else:
            return super(View, self).get_property(name)

    def get_items(self):
        """Get list items per a view

        :rtype: office365.sharepoint.listitems.listItem_collection.ListItemCollection
        """

        def _get_items_inner():
            caml_query = CamlQuery.parse(self.view_query)
            qry = ServiceOperationQuery(self._parent_list, "GetItems", None, caml_query, "query",
                                        self._parent_list.items)
            self.context.add_query(qry)
        self.ensure_property("viewQuery", _get_items_inner)
        return self._parent_list.items

    def delete_object(self):
        """The recommended way to delete a view is to send a DELETE request to the View resource endpoint, as shown
        in View request examples."""
        qry = DeleteEntityQuery(self)
        self.context.add_query(qry)
        self.remove_from_parent_collection()
        return self

    def render_as_html(self):
        result = ClientResult(str)
        qry = ServiceOperationQuery(self, "RenderAsHtml", None, None, None, result)
        self.context.add_query(qry)
        return result

    @property
    def content_type_id(self):
        """Gets the identifier of the content type with which the view is associated.
        :rtype: ContentTypeId
        """
        return self.properties.get("ContentTypeId", ContentTypeId())

    @content_type_id.setter
    def content_type_id(self, value):
        """Sets the identifier of the content type with which the view is associated."""
        self.set_property("ContentTypeId", value)

    @property
    def hidden(self):
        """Gets whether the list view is hidden.
        :rtype: bool or None
        """
        return self.properties.get("Hidden", None)

    @hidden.setter
    def hidden(self, value):
        """Sets whether the list view is hidden.
        """
        self.set_property("Hidden", value)

    @property
    def default_view(self):
        """Gets whether the list view is the default list view.
        :rtype: bool or None
        """
        return self.properties.get("DefaultView", None)

    @default_view.setter
    def default_view(self, value):
        """Sets whether the list view is the default list view.
        """
        self.set_property("DefaultView", value)

    @property
    def view_fields(self):
        """Gets a value that specifies the collection of fields in the list view."""
        return self.properties.get('ViewFields',
                                   ViewFieldCollection(self.context, ResourcePath("ViewFields", self.resource_path)))

    @property
    def view_query(self):
        """Gets or sets a value that specifies the query that is used by the list view."""
        return self.properties.get('ViewQuery', None)

    @property
    def base_view_id(self):
        """Gets a value that specifies the base view identifier of the list view."""
        return self.properties.get('BaseViewId', None)




    def set_property(self, name, value, persist_changes=True):
        super(View, self).set_property(name, value, persist_changes)
        # fallback: create a new resource path
        if self._resource_path is None:
            if name == "Id":
                self._resource_path = ResourcePathServiceOperation(
                    "GetById", [value], self._parent_collection.resource_path)
            elif name == "Title":
                self._resource_path = ResourcePathServiceOperation(
                    "GetByTitle", [value], self._parent_collection.resource_path)
        return self
