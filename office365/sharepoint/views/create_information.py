from office365.runtime.client_value import ClientValue


class ViewCreationInformation(ClientValue):
    """Specifies the properties used to create a new list view."""

    def __init__(self, title=None, view_type_kind=None):
        """
        :param str title: Specifies the display name of the new list view. Its length MUST be equal to or less than 255.
        :param int view_type_kind: Specifies the type of the new list view.
        """
        super(ViewCreationInformation, self).__init__()
        self.Title = title
        self.ViewTypeKind = view_type_kind
        self.ViewFields = None
        self.ViewData = None
        self.RowLimit = None
        self.Query = None
        self.PersonalView = False
        self.Paged = False

    @property
    def entity_type_name(self):
        return "SP.ViewCreationInformation"
