from office365.runtime.client_value import ClientValue


class ViewCreationInformation(ClientValue):
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

    @property
    def entity_type_name(self):
        return "SP.ViewCreationInformation"
