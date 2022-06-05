from office365.runtime.client_value import ClientValue


class ContentTypeInfo(ClientValue):
    """The contentTypeInfo resource indicates the SharePoint content type of an item."""

    def __init__(self, _id=None, name=None):
        self.id = _id
        self.name = name
