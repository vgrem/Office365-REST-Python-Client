from office365.runtime.client_value_object import ClientValueObject


class ViewCreationInformation(ClientValueObject):
    """Specifies the properties used to create a new list view."""

    def __init__(self):
        super(ViewCreationInformation, self).__init__()
        self.Title = None
        self.ViewTypeKind = None
        self.ViewFields = None
        self.ViewData = None
        self.RowLimit = None
        self.Query = None
        self.PersonalView = False
        self.Paged = False

    def to_json(self, data_format):
        return {"parameters": super(ViewCreationInformation, self).to_json(data_format)}

    @property
    def typeName(self):
        return "SP.ViewCreationInformation"
