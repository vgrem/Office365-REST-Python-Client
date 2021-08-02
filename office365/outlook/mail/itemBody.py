from office365.runtime.client_value import ClientValue


class ItemBody(ClientValue):
    """"""

    def __init__(self, content=None, content_type="Text"):
        """

        :type content: str
        :type content_type: str
        """
        super(ItemBody, self).__init__()
        self.content = content
        self.contentType = content_type
