from office365.runtime.client_query import DeleteEntityQuery
from office365.runtime.resource_path import ResourcePath
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.contenttypes.content_type_id import ContentTypeId
from office365.sharepoint.fields.field_collection import FieldCollection


class ContentType(BaseEntity):
    """Specifies a content type."""

    @property
    def id(self):
        """Specifies an identifier for the content type as specified in [MS-WSSTS] section 2.1.2.8.1.
        :rtype: ContentTypeId
        """
        return self.properties.get("Id", ContentTypeId())

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
    def description(self):
        """Gets the description of the content type.
        :rtype: str or None
        """
        return self.properties.get("Description", None)

    @description.setter
    def description(self, value):
        """Sets the description of the content type.
        :rtype: str or None
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
        :rtype: str or None
        """
        self.set_property("Group", value)

    @property
    def schemaXml(self):
        """Specifies the XML schema that represents the content type.
        :rtype: str or None
        """
        return self.properties.get("SchemaXml", None)

    @property
    def fields(self):
        """Gets a value that specifies the collection of fields for the content type."""
        if self.is_property_available('Fields'):
            return self.properties['Fields']
        else:
            return FieldCollection(self.context, ResourcePath("Fields", self.resource_path))

    @property
    def parent(self):
        """Gets the parent content type of the content type."""
        if self.is_property_available('Parent'):
            return self.properties['Parent']
        else:
            return ContentType(self.context, ResourcePath("Parent", self.resource_path))

    def set_property(self, name, value, persist_changes=True):
        super(ContentType, self).set_property(name, value, persist_changes)
        # fallback: create a new resource path
        if name == "StringId" and self._resource_path is None:
            self._resource_path = ResourcePathServiceOperation(
                "getById", [value], self._parent_collection.resource_path)

    def delete_object(self):
        """Deletes the directory object."""
        qry = DeleteEntityQuery(self)
        self.context.add_query(qry)
        self.remove_from_parent_collection()
