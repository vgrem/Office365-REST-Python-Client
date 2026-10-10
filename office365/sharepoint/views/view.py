from __future__ import annotations

from typing import TYPE_CHECKING, Optional, cast

from typing_extensions import Self

from office365.runtime.client_result import ClientResult
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.odata_property import odata
from office365.sharepoint.contenttypes.content_type_id import ContentTypeId
from office365.sharepoint.entity import Entity
from office365.sharepoint.listitems.caml.query import CamlQuery
from office365.sharepoint.listitems.collection import ListItemCollection
from office365.sharepoint.types.resource_path import ResourcePath as SPResPath
from office365.sharepoint.views.field_collection import ViewFieldCollection
from office365.sharepoint.views.visualization.visualization import Visualization

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext
    from office365.sharepoint.documents.gridinitinfotype import GridInitInfoType
    from office365.sharepoint.lists.list import List
    from office365.sharepoint.views.collection import ViewCollection


class View(Entity):
    """Specifies a List View."""

    def __init__(
        self,
        context: ClientContext,
        resource_path: Optional[ResourcePath] = None,
        parent_list: Optional[List] = None,
    ):
        super().__init__(context, resource_path)
        self._parent_list = parent_list

    def get_items(self) -> ListItemCollection:
        """Get list items per a view"""
        assert self.parent_list is not None
        return_type = ListItemCollection(self.context, self.parent_list.items.resource_path)

        def _get_items():
            assert self.parent_list is not None
            assert self.view_query is not None
            caml_query = CamlQuery.parse(self.view_query)
            qry = ServiceOperationQuery(self.parent_list, "GetItems", None, caml_query, "query", return_type)
            self.context.add_query(qry)

        self.ensure_properties(["ViewQuery", "ViewFields"]).after_execute(lambda _: _get_items())
        return return_type

    def render_as_html(self) -> ClientResult[str]:
        """Returns the list view as HTML."""
        return_type = ClientResult[str](self.context)
        qry = ServiceOperationQuery(self, "RenderAsHtml", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def set_view_xml(self, view_xml: str) -> Self:
        """Sets the view schema.

        Args:
            view_xml (str): The view XML to set.
        """
        qry = ServiceOperationQuery(self, "SetViewXml", None, {"viewXml": view_xml})
        self.context.add_query(qry)
        return self

    @property
    def aggregations(self) -> Optional[str]:
        """Specifies fields and functions that define totals shown in a list view."""
        return self.properties.get("Aggregations", None)

    @property
    def aggregations_status(self) -> Optional[str]:
        """
        Specifies whether totals are shown in the list view.
        It MUST be NULL If Aggregations is NULL; otherwise it MUST be "On" or "Off".
        """
        return self.properties.get("AggregationsStatus", None)

    @property
    def associated_content_type_id(self) -> Optional[str]:
        """Represents the content type identifier associated with the view."""
        return self.properties.get("AssociatedContentTypeId", None)

    @property
    def calendar_view_styles(self) -> Optional[str]:
        """Represents an object specifying the style of a SharePoint calendar view."""
        return self.properties.get("CalendarViewStyles", None)

    @property
    def column_width(self) -> Optional[int]:
        """Specifies the width of columns."""
        return self.properties.get("ColumnWidth", None)

    @property
    def parent_list(self) -> Optional[List]:
        """Returns parent List"""
        return self._parent_list

    @property
    def parent_collection(self) -> ViewCollection:
        """Returns parent ViewCollection.

        Raises:
            ValueError: If parent collection is not initialized
        """
        from office365.sharepoint.views.collection import ViewCollection

        if self._parent_collection is None:
            raise ValueError("Parent collection is not initialized")
        return cast(ViewCollection, self._parent_collection)

    @property
    def js_link(self) -> Optional[str]:
        """Specifies the JavaScript files used for the view."""
        return self.properties.get("JSLink", None)

    @odata(name="ContentTypeId")
    @property
    def content_type_id(self) -> Optional[ContentTypeId]:
        """Gets the identifier of the content type with which the view is associated."""
        return self.properties.get("ContentTypeId", ContentTypeId())

    @content_type_id.setter
    def content_type_id(self, value):
        """Sets the identifier of the content type with which the view is associated."""
        self.set_property("ContentTypeId", value)

    @property
    def custom_formatter(self) -> Optional[str]:
        """Specifies the Custom Formatter used for the view."""
        return self.properties.get("CustomFormatter", None)

    @property
    def custom_order(self) -> Optional[str]:
        """"""
        return self.properties.get("CustomOrder", None)

    @property
    def editor_modified(self) -> Optional[bool]:
        """Specifies whether the list view was modified in an editor."""
        return self.properties.get("EditorModified", None)

    def formats(self) -> Optional[str]:
        """Specifies the column and row formatting for the list view."""
        return self.properties.get("Formats", None)

    @odata(name="Hidden")
    @property
    def hidden(self) -> Optional[bool]:
        """Gets whether the list view is hidden."""
        return self.properties.get("Hidden", None)

    @hidden.setter
    def hidden(self, value: bool) -> None:
        """Sets whether the list view is hidden."""
        self.set_property("Hidden", value)

    @odata(name="DefaultView")
    @property
    def default_view(self) -> Optional[bool]:
        """Gets whether the list view is the default list view."""
        return self.properties.get("DefaultView", None)

    @default_view.setter
    def default_view(self, value: bool) -> None:
        """Sets whether the list view is the default list view."""
        self.set_property("DefaultView", value)

    @odata(name="DefaultViewForContentType")
    @property
    def default_view_for_content_type(self) -> Optional[bool]:
        """Specifies whether the list view is the default list view for the content type specified by ContentTypeId."""
        return self.properties.get("DefaultViewForContentType", None)

    @odata(name="ViewFields")
    @property
    def view_fields(self) -> ViewFieldCollection:
        """Gets a value that specifies the collection of fields in the list view."""
        return self.properties.get(
            "ViewFields",
            ViewFieldCollection(self.context, ResourcePath("ViewFields", self.resource_path)),
        )

    @property
    def view_query(self) -> Optional[str]:
        """Gets or sets a value that specifies the query that is used by the list view."""
        return self.properties.get("ViewQuery", None)

    @property
    def base_view_id(self) -> Optional[str]:
        """Gets a value that specifies the base view identifier of the list view."""
        return self.properties.get("BaseViewId", None)

    def read_only_view(self) -> Optional[bool]:
        """Specifies whether the list view is read-only."""
        return self.properties.get("ReadOnlyView", None)

    @odata(name="ServerRelativePath")
    @property
    def server_relative_path(self) -> Optional[SPResPath]:
        """Gets the server-relative Path of the View."""
        return self.properties.get("ServerRelativePath", SPResPath())

    @property
    def view_joins(self) -> Optional[str]:
        """Specifies the joins that are used in the list view"""
        return self.properties.get("ViewJoins", None)

    @odata(name="VisualizationInfo")
    @property
    def visualization_info(self) -> Visualization:
        """Specifies how the view is layed out."""
        return self.properties.get("VisualizationInfo", Visualization())

    @property
    def id(self) -> Optional[str]:
        """Gets the view identifier."""
        return self.properties.get("Id", None)

    @property
    def title(self) -> Optional[str]:
        """Gets the view title."""
        return self.properties.get("Title", None)

    @title.setter
    def title(self, value: str) -> None:
        """Sets the view title."""
        self.set_property("Title", value)

    @odata(name="ServerRelativeUrl")
    @property
    def server_relative_url(self) -> Optional[str]:
        """Gets the server-relative URL of the view."""
        return self.properties.get("ServerRelativeUrl", None)

    @odata(name="ViewType")
    @property
    def view_type(self) -> Optional[str]:
        """Gets the type of the view (HTML, Grid, Calendar, etc.)."""
        return self.properties.get("ViewType", None)

    @odata(name="RowLimit")
    @property
    def row_limit(self) -> Optional[int]:
        """Gets the maximum number of items per page."""
        return self.properties.get("RowLimit", None)

    @row_limit.setter
    def row_limit(self, value: int) -> None:
        """Sets the maximum number of items per page."""
        self.set_property("RowLimit", value)

    @odata(name="Paged")
    @property
    def paged(self) -> Optional[bool]:
        """Gets whether the view supports paging."""
        return self.properties.get("Paged", None)

    @odata(name="PersonalView")
    @property
    def personal_view(self) -> Optional[bool]:
        """Gets whether this is a personal (user-specific) view."""
        return self.properties.get("PersonalView", None)

    @odata(name="OrderedView")
    @property
    def ordered_view(self) -> Optional[bool]:
        """Gets whether the view is ordered."""
        return self.properties.get("OrderedView", None)

    @property
    def grid_init_info(self) -> GridInitInfoType:
        """Gets the GridInitInfo property"""
        from office365.sharepoint.documents.gridinitinfotype import GridInitInfoType

        return self.properties.get("GridInitInfo", GridInitInfoType())

    @property
    def grid_layout(self) -> Optional[str]:
        """Gets the GridLayout property"""
        return self.properties.get("GridLayout", None)

    @property
    def html_schema_xml(self) -> Optional[str]:
        """Gets the HtmlSchemaXml property"""
        return self.properties.get("HtmlSchemaXml", None)

    @property
    def image_url(self) -> Optional[str]:
        """Gets the ImageUrl property"""
        return self.properties.get("ImageUrl", None)

    @property
    def include_root_folder(self) -> Optional[bool]:
        """Gets the IncludeRootFolder property"""
        return self.properties.get("IncludeRootFolder", None)

    @property
    def list_view_xml(self) -> Optional[str]:
        """Gets the ListViewXml property"""
        return self.properties.get("ListViewXml", None)

    @property
    def method(self) -> Optional[str]:
        """Gets the Method property"""
        return self.properties.get("Method", None)

    @property
    def mobile_default_view(self) -> Optional[bool]:
        """Gets the MobileDefaultView property"""
        return self.properties.get("MobileDefaultView", None)

    @property
    def mobile_view(self) -> Optional[bool]:
        """Gets the MobileView property"""
        return self.properties.get("MobileView", None)

    @property
    def moderation_type(self) -> Optional[str]:
        """Gets the ModerationType property"""
        return self.properties.get("ModerationType", None)

    @property
    def new_document_templates(self) -> Optional[str]:
        """Gets the NewDocumentTemplates property"""
        return self.properties.get("NewDocumentTemplates", None)

    @property
    def page_render_type(self) -> Optional[int]:
        """Gets the PageRenderType property"""
        return self.properties.get("PageRenderType", None)

    @property
    def view_projected_fields(self) -> Optional[str]:
        """Gets the ViewProjectedFields property"""
        return self.properties.get("ViewProjectedFields", None)

    @property
    def requires_client_integration(self) -> Optional[bool]:
        """Gets the RequiresClientIntegration property"""
        return self.properties.get("RequiresClientIntegration", None)

    @property
    def scope(self) -> Optional[int]:
        """Gets the Scope property"""
        return self.properties.get("Scope", None)

    @property
    def style_id(self) -> Optional[str]:
        """Gets the StyleId property"""
        return self.properties.get("StyleId", None)

    @property
    def tabular_view(self) -> Optional[bool]:
        """Gets the TabularView property"""
        return self.properties.get("TabularView", None)

    @property
    def threaded(self) -> Optional[bool]:
        """Gets the Threaded property"""
        return self.properties.get("Threaded", None)

    @property
    def toolbar(self) -> Optional[str]:
        """Gets the Toolbar property"""
        return self.properties.get("Toolbar", None)

    @property
    def toolbar_template_name(self) -> Optional[str]:
        """Gets the ToolbarTemplateName property"""
        return self.properties.get("ToolbarTemplateName", None)

    @property
    def view_data(self) -> Optional[str]:
        """Gets the ViewData property"""
        return self.properties.get("ViewData", None)

    @property
    def view_type2(self) -> Optional[str]:
        """Gets the ViewType2 property"""
        return self.properties.get("ViewType2", None)
