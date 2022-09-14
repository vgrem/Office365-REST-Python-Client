from office365.runtime.client_value import ClientValue


class HyperlinkOrPictureColumn(ClientValue):
    """Represents a hyperlink or picture column in SharePoint."""

    def __init__(self, is_picture=None):
        self.isPicture = is_picture
