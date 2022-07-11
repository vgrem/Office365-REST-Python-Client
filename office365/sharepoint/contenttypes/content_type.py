from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.contenttypes.content_type_id import ContentTypeId
from office365.sharepoint.contenttypes.field_link_collection import FieldLinkCollection
from office365.sharepoint.fields.collection import FieldCollection


class ContentType(BaseEntity):
    """Specifies a content type."""

    def reorder_fields(self, field_names):
        """
        The ReorderFields method is called to change the order in which fields appear in a content type.

        :param list[str] field_names:
        """
        qry = ServiceOperationQuery(self, "ReorderFields", field_names)
        self.context.add_query(qry)
        return self

    def update(self, update_children):
        """
        Updates the content type, and any child objects  of the content type if specified,
        with any changes made to the content type.

        :param bool update_children: Specifies whether changes propagate to child objects of the content type.
        """
        super(ContentType, self).update()
        if update_children:
            qry = ServiceOperationQuery(self, "Update", [update_children])
            self.context.add_query(qry)
        return self

    @property
    def id(self):
        """Specifies an identifier for the content type as specified in [MS-WSSTS] section 2.1.2.8.1.
        :rtype: ContentTypeId
        """
        return self.properties.get("Id", ContentTypeId())

    @property
    def string_id(self):
        """A string representation of the value of the Id
        :rtype: str
        """
        return self.properties.get("StringId", None)

    @property
    def name(self):
        """Gets the name of the content type.
        :rtype: str or None
        """
        return self.properties.get("Name", None)

    @name.setter
    def name(self, value):
        """Sets the name of the content type.
        :rtype: str or None
        """
        self.set_property("Name", value)

    @property
    def new_form_client_side_component_properties(self):
        """
        :rtype: str or None
        """
        return self.properties.get("NewFormClientSideComponentProperties", None)

    @property
    def description(self):
        """Gets the description of the content type.
        :rtype: str or None
        """
        return self.properties.get("Description", None)

    @description.setter
    def description(self, value):
        """Sets the description of the content type.

        :type value: str
        """
        self.set_property("Description", value)

    @property
    def group(self):
        """Gets the group of the content type.

        :rtype: str or None
        """
        return self.properties.get("Group", None)

    @group.setter
    def group(self, value):
        """Sets the group of the content type.

        :type value: str
        """
        self.set_property("Group", value)

    @property
    def schema_xml(self):
        """Specifies the XML schema that represents the content type.

        :rtype: str or None
        """
        return self.properties.get("SchemaXml", None)

    @property
    def fields(self):
        """Gets a value that specifies the collection of fields for the content type."""
        return self.properties.get('Fields',
                                   FieldCollection(self.context, ResourcePath("Fields", self.resource_path)))

    @property
    def parent(self):
        """Gets the parent content type of the content type."""
        return self.properties.get('Parent',
                                   ContentType(self.context, ResourcePath("Parent", self.resource_path)))

    @property
    def field_links(self):
        """Specifies the collection of field links for the content type."""
        return self.properties.get('FieldLinks',
                                   FieldLinkCollection(self.context, ResourcePath("FieldLinks", self.resource_path)))

    def get_property(self, name, default_value=None):
        if name == "FieldLinks":
            default_value = self.field_links
        return super(ContentType, self).get_property(name, default_value)

    def set_property(self, name, value, persist_changes=True):
        super(ContentType, self).set_property(name, value, persist_changes)
        # fallback: create a new resource path
        if name == "StringId" and self._resource_path is None:
            self._resource_path = self.parent_collection.get_by_id(value).resource_path
        return self
