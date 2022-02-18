from office365.runtime.client_path import ClientPath


class ResourcePathUrl(ClientPath):
    """Resource path for OneDrive path-based addressing"""

    def __init__(self, rel_url, parent):
        """
        :param str rel_url: File or Folder relative url
        :type parent: office365.runtime.client_path.ClientPath
        """
        super(ResourcePathUrl, self).__init__(rel_url, parent)
        self._nested = False

    @property
    def segments(self):
        cur_delimiter = "/" if self._nested else self.delimiter
        if isinstance(self.parent, ResourcePathUrl):
            self.parent._nested = True
            return [self._name, cur_delimiter]
        else:
            return [self.delimiter, self._name, cur_delimiter]

    @property
    def delimiter(self):
        return ":/"
