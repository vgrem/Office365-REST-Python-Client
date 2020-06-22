from office365.runtime.clientValue import ClientValue
from office365.runtime.clientValueCollection import ClientValueCollection
from office365.sharepoint.fields.field import Field
from office365.sharepoint.fields.fieldType import FieldType


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
        type_name = Field.get_field_type(self.FieldTypeKind).__name__
        return "SP.{0}".format(type_name)
