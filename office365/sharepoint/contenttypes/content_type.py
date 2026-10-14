from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional

from typing_extensions import Self

from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.odata_property import odata
from office365.sharepoint.contenttypes.content_type_id import ContentTypeId
from office365.sharepoint.contenttypes.fieldlinks.collection import FieldLinkCollection
from office365.sharepoint.entity import Entity
from office365.sharepoint.entity_collection import EntityCollection
from office365.sharepoint.fields.collection import FieldCollection
from office365.sharepoint.translation.user_resource import UserResource

if TYPE_CHECKING:
    from office365.sharepoint.workflow.associations.association import (
        WorkflowAssociation,
    )


def _content_type_order_ids(order: Any) -> List[str]:
    """Extract the content-type id strings from a list folder's order value.

    The server returns an order as ``Collection(SP.ContentTypeId)``. Depending
    on how the folder property is typed it reaches us either as a
    ``ClientValueCollection`` of ``ContentTypeId`` or as a single
    ``ContentTypeId`` that flattened the array under numeric keys.
    """
    if order is None:
        return []
    source = vars(order) if not isinstance(order, dict) else order
    indexed = sorted((k for k in source if str(k).isdigit()), key=int)
    if indexed:
        items: List[Any] = [source[k] for k in indexed]
    elif isinstance(order, dict):
        items = [order]
    else:
        items = list(order) if hasattr(order, "__iter__") else [order]
    result: List[str] = []
    for item in items:
        value = item.get("StringValue") if isinstance(item, dict) else getattr(item, "StringValue", None)
        if value:
            result.append(value)
    return result


class ContentType(Entity):
    """
    Specifies a content type.

    A named and uniquely identifiable collection of settings and fields that store metadata for individual items
    in a SharePoint list. One or more content types can be associated with a list, which restricts the contents
    to items of those types
    """

    def __str__(self):
        return self.name or self.entity_type_name

    def __repr__(self):
        return self.string_id or str(self.id) or self.entity_type_name

    def reorder_fields(self, field_names: List[str]) -> Self:
        """The ReorderFields method is called to change the order in which fields appear in a content type.

        Args:
            field_names (list[str]): Rearranges the collection of fields in the order in which field internal names are
                specified.
        """
        payload = {"fieldNames": list(field_names)}
        qry = ServiceOperationQuery(self, "ReorderFields", None, payload)
        self.context.add_query(qry)
        return self

    def set_default(self, value: bool = True) -> Self:
        """Set whether this content type is the default for its parent list.

        A list designates its default content type as the first entry of the
        list root folder's ``UniqueContentTypeOrder``. This rewrites that order
        so this (list-scoped) content type comes first; the change is submitted
        with the next ``execute_query()``.

        Args:
            value (bool): ``True`` (default) moves this content type to the
                front of the list's content type order (making it the default),
                ``False`` moves it to the end.

        Example:
            >>> list_ct = target_list.content_types.get_by_id(ct_id)
            >>> list_ct.set_default().execute_query()
        """
        from office365.sharepoint.lists.list import List

        parent = self.parent_collection.parent if self.parent_collection is not None else None
        if not isinstance(parent, List):
            raise ValueError(
                "set_default() is supported only for a list-scoped content type "
                "(for example, one obtained from list.content_types)"
            )
        target_id = self.string_id or self.id.StringValue
        if not target_id:
            raise ValueError("set_default() requires a loaded content type (missing StringId)")
        root_folder = parent.root_folder

        def _reorder(_folder: Any) -> None:
            explicit = _content_type_order_ids(root_folder.properties.get("UniqueContentTypeOrder"))
            order = explicit or _content_type_order_ids(root_folder.properties.get("ContentTypeOrder"))
            order = [content_type_id for content_type_id in order if content_type_id != target_id]
            if value:
                order.insert(0, target_id)
            else:
                order.append(target_id)
            collection = ClientValueCollection(ContentTypeId)
            for content_type_id in order:
                collection.add(ContentTypeId(StringValue=content_type_id))
            root_folder.set_property("UniqueContentTypeOrder", collection)
            root_folder.update()

        root_folder.ensure_properties(["ContentTypeOrder", "UniqueContentTypeOrder"]).after_execute(_reorder)
        return self

    def update(self, *args: Any, update_children: bool = False) -> Self:
        """Updates the content type, and any child objects  of the content type if specified,
        with any changes made to the content type.

        Args:
            update_children (bool): Specifies whether changes propagate to child objects of the content type.
        """
        super().update()
        if update_children:
            payload = {"updateChildren": update_children}
            qry = ServiceOperationQuery(self, "Update", None, payload)
            self.context.add_query(qry)
        return self

    @property
    def client_form_custom_formatter(self) -> Optional[str]:
        return self.properties.get("ClientFormCustomFormatter", None)

    @property
    def display_form_client_side_component_id(self) -> Optional[str]:
        """
        The component ID of an SPFx Form Customizer to connect to this content type for usage with display forms.
        """
        return self.properties.get("DisplayFormClientSideComponentId", None)

    @property
    def display_form_client_side_component_properties(self) -> Optional[str]:
        """
        The component properties of an SPFx Form Customizer to connect to this content type for usage with display forms
        """
        return self.properties.get("DisplayFormClientSideComponentProperties", None)

    @property
    def display_form_template_name(self) -> Optional[str]:
        """
        Specifies the name of a custom display form template to use for list items that have been assigned
        the content type.
        """
        return self.properties.get("DisplayFormTemplateName", None)

    @property
    def display_form_url(self) -> Optional[str]:
        """
        Specifies the URL of a custom display form to use for list items that have been assigned the content type.
        """
        return self.properties.get("DisplayFormUrl", None)

    @property
    def edit_form_client_side_component_id(self) -> Optional[str]:
        """
        The component properties of an SPFx Form Customizer to connect to this content type for usage with edit item
            forms
        """
        return self.properties.get("EditFormClientSideComponentId", None)

    @property
    def edit_form_client_side_component_properties(self) -> Optional[str]:
        """
        The component ID of an SPFx Form Customizer to connect to this content type for usage with edit item forms
        """
        return self.properties.get("EditFormClientSideComponentProperties", None)

    @property
    def id(self) -> ContentTypeId:
        """
        Specifies an identifier for the content type as specified in [MS-WSSTS] section 2.1.2.8.1.
        """
        return self.properties.get("Id", ContentTypeId())

    @property
    def scope(self) -> Optional[str]:
        """Specifies a server-relative path to the content type scope of the content type."""
        return self.properties.get("Scope", None)

    @property
    def sealed(self) -> Optional[bool]:
        """Specifies whether the content type can be changed."""
        return self.properties.get("Sealed", None)

    @property
    def string_id(self) -> Optional[str]:
        """A string representation of the value of the Id"""
        return self.properties.get("StringId", None)

    @property
    def name(self) -> Optional[str]:
        """Gets the name of the content type."""
        return self.properties.get("Name", None)

    @name.setter
    def name(self, value: str) -> None:
        """Sets the name of the content type."""
        self.set_property("Name", value)

    @property
    def new_form_client_side_component_properties(self) -> Optional[str]:
        """The component properties of an SPFx Form Customizer to connect to this content type for usage with new
        item forms"""
        return self.properties.get("NewFormClientSideComponentProperties", None)

    @property
    def new_form_url(self) -> Optional[str]:
        """Specifies the URL of a custom new form to use for list items that have been assigned the content type."""
        return self.properties.get("NewFormUrl", None)

    @property
    def description(self) -> Optional[str]:
        """Gets the description of the content type."""
        return self.properties.get("Description", None)

    @description.setter
    def description(self, value: str) -> None:
        """Sets the description of the content type."""
        self.set_property("Description", value)

    @odata(name="DescriptionResource")
    @property
    def description_resource(self):
        """Gets the SP.UserResource object (section 3.2.5.333) for the description of this content type"""
        return self.properties.get(
            "DescriptionResource",
            UserResource(self.context, ResourcePath("DescriptionResource", self.resource_path)),
        )

    @property
    def document_template(self) -> Optional[str]:
        """Specifies the file path to the document template (1) used for a new list item that has been assigned
        the content type.
        """
        return self.properties.get("DocumentTemplate", None)

    @property
    def document_template_url(self) -> Optional[str]:
        """Specifies the URL of the document template assigned to the content type."""
        return self.properties.get("DocumentTemplateUrl", None)

    @property
    def edit_form_url(self) -> Optional[str]:
        """
        Specifies the URL of a custom edit form to use for list items that have been assigned the content type.
        """
        return self.properties.get("EditFormUrl", None)

    @property
    def group(self) -> Optional[str]:
        """Gets the group of the content type."""
        return self.properties.get("Group", None)

    @group.setter
    def group(self, value: str) -> None:
        """Sets the group of the content type."""
        self.set_property("Group", value)

    @property
    def hidden(self) -> Optional[bool]:
        """Specifies whether the content type is unavailable for creation or usage directly from a user interface."""
        return self.properties.get("Hidden", None)

    @property
    def js_link(self) -> Optional[str]:
        """Gets or sets the JSLink for the content type custom form template"""
        return self.properties.get("JSLink", None)

    @property
    def read_only(self) -> Optional[bool]:
        """Specifies whether changes to the content type properties are denied."""
        return self.properties.get("ReadOnly", None)

    @odata(name="NameResource")
    @property
    def name_resource(self):
        """Specifies the SP.UserResource object for the name of this content type"""
        return self.properties.get(
            "NameResource",
            UserResource(self.context, ResourcePath("NameResource", self.resource_path)),
        )

    @property
    def schema_xml(self) -> Optional[str]:
        """Specifies the XML schema that represents the content type."""
        return self.properties.get("SchemaXml", None)

    @property
    def fields(self) -> FieldCollection:
        """Gets a value that specifies the collection of fields for the content type."""
        return self.properties.get(
            "Fields",
            FieldCollection(self.context, ResourcePath("Fields", self.resource_path)),
        )

    @property
    def parent(self) -> "ContentType":
        """Gets the parent content type of the content type."""
        return self.properties.get(
            "Parent",
            ContentType(self.context, ResourcePath("Parent", self.resource_path)),
        )

    @odata(name="FieldLinks")
    @property
    def field_links(self) -> FieldLinkCollection:
        """Specifies the collection of field links for the content type."""
        return self.properties.get(
            "FieldLinks",
            FieldLinkCollection(self.context, ResourcePath("FieldLinks", self.resource_path)),
        )

    @property
    def property_ref_name(self):
        return "StringId"

    @property
    def display_form_target(self) -> Optional[int]:
        """Gets the DisplayFormTarget property"""
        return self.properties.get("DisplayFormTarget", None)

    @property
    def edit_form_target(self) -> Optional[int]:
        """Gets the EditFormTarget property"""
        return self.properties.get("EditFormTarget", None)

    @property
    def edit_form_template_name(self) -> Optional[str]:
        """Gets the EditFormTemplateName property"""
        return self.properties.get("EditFormTemplateName", None)

    @property
    def mobile_display_form_url(self) -> Optional[str]:
        """Gets the MobileDisplayFormUrl property"""
        return self.properties.get("MobileDisplayFormUrl", None)

    @property
    def mobile_edit_form_url(self) -> Optional[str]:
        """Gets the MobileEditFormUrl property"""
        return self.properties.get("MobileEditFormUrl", None)

    @property
    def mobile_new_form_url(self) -> Optional[str]:
        """Gets the MobileNewFormUrl property"""
        return self.properties.get("MobileNewFormUrl", None)

    @property
    def new_form_client_side_component_id(self) -> Optional[str]:
        """Gets the NewFormClientSideComponentId property"""
        return self.properties.get("NewFormClientSideComponentId", None)

    @property
    def new_form_target(self) -> Optional[int]:
        """Gets the NewFormTarget property"""
        return self.properties.get("NewFormTarget", None)

    @property
    def new_form_template_name(self) -> Optional[str]:
        """Gets the NewFormTemplateName property"""
        return self.properties.get("NewFormTemplateName", None)

    @property
    def schema_xml_with_resource_tokens(self) -> Optional[str]:
        """Gets the SchemaXmlWithResourceTokens property"""
        return self.properties.get("SchemaXmlWithResourceTokens", None)

    @property
    def workflow_associations(self) -> EntityCollection[WorkflowAssociation]:
        """Gets the WorkflowAssociations property"""
        from office365.sharepoint.workflow.associations.association import (
            WorkflowAssociation,
        )

        return self.properties.get(
            "WorkflowAssociations",
            EntityCollection[WorkflowAssociation](
                self.context, WorkflowAssociation, ResourcePath("WorkflowAssociations", self.resource_path)
            ),
        )
