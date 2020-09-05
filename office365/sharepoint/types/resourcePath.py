from office365.runtime.client_value import ClientValue


class ResourcePath(ClientValue):

    def __init__(self, decodedUrl):
        super().__init__()
        self.DecodedUrl = decodedUrl
