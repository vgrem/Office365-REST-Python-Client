from office365.runtime.client_value import ClientValue


class ItemBody(ClientValue):
    """"""

    def __init__(self, content, contentType="Text"):
        """

        :type content: str
        :type contentType: str
        """
        super(ItemBody, self).__init__()
        self.content = content
        self.contentType = contentType
