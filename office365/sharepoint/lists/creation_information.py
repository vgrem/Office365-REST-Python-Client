from office365.runtime.client_value import ClientValue


class ListCreationInformation(ClientValue):
    """Represents metadata about list creation."""

    def __init__(self, title=None, description=None, base_template=None, allow_content_types=False):
        """

        :type base_template: int or None
        :type allow_content_types: bool
        :type description: str or None
        :type title: str
        """
        super(ListCreationInformation, self).__init__()
        self.Title = title
        self.Description = description
        self.BaseTemplate = base_template
        self.AllowContentTypes = allow_content_types

    @property
    def entity_type_name(self):
        return "SP.List"
