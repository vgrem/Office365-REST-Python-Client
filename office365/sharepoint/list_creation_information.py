from office365.runtime.client_value_object import ClientValueObject


class ListCreationInformation(ClientValueObject):
    """Represents metadata about list creation."""

    def __init__(self, title=None, description=None, base_template=None, allow_content_types=False):
        super(ListCreationInformation, self).__init__()
        self.Title = title
        self.Description = description
        self.BaseTemplate = base_template
        self.AllowContentTypes = allow_content_types

    @property
    def entityTypeName(self):
        return "SP.List"
