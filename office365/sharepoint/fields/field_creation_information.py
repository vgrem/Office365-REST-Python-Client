from office365.runtime.clientValue import ClientValue


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
        self.Choices = None
        self.LookupListId = None
        self.LookupFieldName = None
        self.LookupWebId = None
        self.Required = None

    @property
    def entity_type_name(self):
        return "SP.Field"
