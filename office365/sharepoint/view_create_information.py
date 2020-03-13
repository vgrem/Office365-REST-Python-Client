from office365.runtime.client_value_object import ClientValueObject


class ViewCreationInformation(ClientValueObject):
    """Specifies the properties used to create a new list view."""

    def __init__(self):
        super(ViewCreationInformation, self).__init__()
        self.Title = None

    @property
    def typeName(self):
        return "SP.View"
