from office365.runtime.client_value_object import ClientValueObject


class ListCreationInformation(ClientValueObject):
    """Represents metadata about list creation."""

    def __init__(self):
        super(ListCreationInformation, self).__init__()
        self.Title = None
        self.Description = None
        self.BaseTemplate = None
        self.AllowContentTypes = False
        self.metadata_type = "SP.List"

