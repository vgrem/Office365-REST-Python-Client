from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.sharepoint.fields.field import Field
from office365.sharepoint.fields.field_type import FieldType


class FieldCreationInformation(ClientValue):

    def __init__(self, title, field_type_kind, description=None,
                 lookup_list_id=None, lookup_field_name=None, lookup_web_id=None,
                 required=False):
        """
        Represents metadata about fields creation.

        :type lookup_web_id: str
        :type required: bool
        :type lookup_field_name: str
        :type lookup_list_id: str
        :type title: str
        :type field_type_kind: int
        :type description: str or None
        """
        super(FieldCreationInformation, self).__init__()
        self.Title = title
        self.FieldTypeKind = field_type_kind
        self.Description = description
        self.Choices = ClientValueCollection(str) \
            if field_type_kind == FieldType.MultiChoice or field_type_kind == FieldType.Choice else None
        self.LookupListId = lookup_list_id
        self.LookupFieldName = lookup_field_name
        self.LookupWebId = lookup_web_id
        self.Required = required

    @property
    def entity_type_name(self):
        return "SP.FieldCreationInformation"
