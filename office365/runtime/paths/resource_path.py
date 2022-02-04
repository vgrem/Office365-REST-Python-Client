from office365.runtime.client_path import ClientPath


class ResourcePath(ClientPath):
    """OData resource path"""

    def __init__(self, name, parent=None):
        """

        :param str name: entity or property name
        :type parent: office365.runtime.client_path.ClientPath or None
        """
        super().__init__(parent)
        self._name = name
        self._parent = parent

    @property
    def segments(self):
        return [self.delimiter, self._name]
