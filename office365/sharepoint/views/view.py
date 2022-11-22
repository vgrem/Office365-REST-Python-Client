from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.contenttypes.content_type_id import ContentTypeId
from office365.sharepoint.listitems.caml.query import CamlQuery
from office365.sharepoint.listitems.collection import ListItemCollection
from office365.sharepoint.views.field_collection import ViewFieldCollection
from office365.sharepoint.types.resource_path import ResourcePath as SPResPath
from office365.sharepoint.views.visualization import Visualization


class View(BaseEntity):
    """Specifies a List View."""

    def __init__(self, context, resource_path=None, parent_list=None):
        """
        :type parent_list: office365.sharepoint.lists.list.List or None
        """
        super(View, self).__init__(context, resource_path)
        self._parent_list = parent_list

    def get_items(self):
        """Get list items per a view"""
        return_type = ListItemCollection(self.context, self.parent_list.items.resource_path)

        def _get_items_inner():
            caml_query = CamlQuery.parse(self.view_query)
            qry = ServiceOperationQuery(self.parent_list, "GetItems", None, caml_query, "query", return_type)
            self.context.add_query(qry)
        self.ensure_property("ViewQuery", _get_items_inner)
        return return_type

    def render_as_html(self):
        """
        Returns the list view as HTML.
        """
        return_type = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "RenderAsHtml", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def set_view_xml(self, view_xml):
        """
        Sets the view schema.

        :param str view_xml: The view XML to set.
        """
        qry = ServiceOperationQuery(self, "SetViewXml", None, {"viewXml": view_xml})
        self.context.add_query(qry)
        return self

    @property
    def parent_list(self):
        """Returns parent List"""
        return self._parent_list

    @property
    def parent_collection(self):
        """
        :rtype: office365.sharepoint.views.collection.ViewCollection
        """
        return self._parent_collection

    @property
    def js_link(self):
        """
        Specifies the JavaScript files used for the view.

        :rtype: str or None
        """
        return self.properties.get('JSLink', None)

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
    def editor_modified(self):
        """Specifies whether the list view was modified in an editor."""
        return self.properties.get("EditorModified", None)

    def formats(self):
        """Specifies the column and row formatting for the list view.

        :stype: str or None
        """
        return self.properties.get("Formats", None)

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

    def read_only_view(self):
        """Specifies whether the list view is read-only."""
        return self.properties.get('ReadOnlyView', None)

    @property
    def server_relative_path(self):
        """Gets the server-relative Path of the View.
        """
        return self.properties.get("ServerRelativePath", SPResPath())

    @property
    def view_joins(self):
        """Specifies the joins that are used in the list view."""
        return self.properties.get("ViewJoins", None)

    @property
    def visualization_info(self):
        """Specifies how the view is layed out."""
        return self.properties.get("VisualizationInfo", Visualization())

    def get_property(self, name, default_value=None):
        property_mapping = {
            "ViewFields": self.view_fields,
            "DefaultView": self.default_view,
            "ServerRelativePath": self.server_relative_path,
            "VisualizationInfo": self.visualization_info
        }
        if name in property_mapping:
            default_value = property_mapping[name]
        return super(View, self).get_property(name, default_value)

    def set_property(self, name, value, persist_changes=True):
        super(View, self).set_property(name, value, persist_changes)
        # fallback: create a new resource path
        if self._resource_path is None:
            if name == "Id":
                self._resource_path = self.parent_collection.get_by_id(value).resource_path
        return self
