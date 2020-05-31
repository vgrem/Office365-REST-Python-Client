from office365.runtime.client_value_object import ClientValueObject


class FieldCreationInformation(ClientValueObject):
    """Represents metadata about field creation."""

    def __init__(self, title, field_type_kind, description=None):
        super(FieldCreationInformation, self).__init__()
        self.Title = title
        self.FieldTypeKind = field_type_kind
        self.Description = description

    @property
    def entity_type_name(self):
        return "SP.Field"
