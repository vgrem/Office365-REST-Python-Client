from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_query import CreateEntityQuery
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.sharepoint.fields.field import Field


class FieldCollection(ClientObjectCollection):
    """Represents a collection of Field resource."""

    def __init__(self, context, resource_path=None):
        super(FieldCollection, self).__init__(context, Field, resource_path)

    def create_typed_object(self, properties):
        field = super(FieldCollection, self).create_typed_object(properties)
        return field

    def add(self, field_creation_information):
        """Adds a fields to the fields collection.

        :type field_creation_information: FieldCreationInformation
        """
        field = Field.create_field_from_type(self.context, field_creation_information.FieldTypeKind)
        self.add_child(field)
        qry = CreateEntityQuery(self, field_creation_information, field)
        self.context.add_query(qry)
        return field

    def get_by_id(self, _id):
        """Gets the fields with the specified ID."""
        return Field(self.context, ResourcePathServiceOperation("getById", [_id], self.resource_path))

    def get_by_internal_name_or_title(self, name_title):
        """Returns the first Field object with the specified internal name or title from the collection.

        :type name_title: str
        """
        return Field(self.context,
                     ResourcePathServiceOperation("getByInternalNameOrTitle", [name_title], self.resource_path))

    def get_by_title(self, title):
        """Returns the first fields object in the collection based on the title of the specified fields.

        :type title: str
        """
        return Field(self.context,
                     ResourcePathServiceOperation("getByTitle", [title], self.resource_path))
