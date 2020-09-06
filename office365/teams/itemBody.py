from office365.runtime.client_value import ClientValue


class ItemBody(ClientValue):

    def __init__(self, content, contentType=None):
        """

        :type content: str
        :type contentType: str
        """
        super().__init__()
        self.content = content
        self.contentType = contentType
