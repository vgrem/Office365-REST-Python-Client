from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.sharepoint.fields.field import Field
from office365.sharepoint.fields.field_type import FieldType


class FieldCreationInformation(ClientValue):

    def __init__(self, title, field_type_kind, description=None):
        """
        Represents metadata about fields creation.

        :type title: str
        """
        super(FieldCreationInformation, self).__init__()
        self.Title = title
        self.FieldTypeKind = field_type_kind
        self.Description = description
        self.Choices = field_type_kind == FieldType.MultiChoice and ClientValueCollection(str) or None
        self.LookupListId = None
        self.LookupFieldName = None
        self.LookupWebId = None
        self.Required = None

    @property
    def entity_type_name(self):
        type_name = Field.resolve_field_type(self.FieldTypeKind).__name__
        return "SP.{0}".format(type_name)
