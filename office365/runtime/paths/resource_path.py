from office365.runtime.client_path import ClientPath


class ResourcePath(ClientPath):
    """OData resource path"""

    @property
    def segments(self):
        return [self.delimiter, self._name]

    @property
    def delimiter(self):
        return "/"
