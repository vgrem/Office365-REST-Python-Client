from office365.runtime.client_path import ClientPath


class ResourcePathUrl(ClientPath):
    """Resource path for OneDrive path-based addressing"""

    def __init__(self, rel_url, parent):
        """
        :param str rel_url: File or Folder relative url
        :type parent: office365.runtime.client_path.ClientPath
        """
        super(ResourcePathUrl, self).__init__(parent)
        self._url = rel_url
        self._nested = False

    @property
    def segments(self):
        delimiter = "/" if self._nested else ":/"
        if isinstance(self.parent, ResourcePathUrl):
            self.parent._nested = True
            return [self._url, delimiter]
        else:
            return [self.delimiter, self._url, delimiter]

    @property
    def delimiter(self):
        return ":/"

    @property
    def name(self):
        return self._url
