from office365.runtime.paths.entity import EntityPath


class UrlPath(EntityPath):
    """Resource path for OneDrive entity path-based addressing"""

    def __init__(self, url, parent):
        """
        :param str url: File or Folder server relative url
        :type parent: office365.runtime.paths.ResourcePath
        """
        super(UrlPath, self).__init__(url, parent)
        self._nested = False

    @property
    def collection(self):
        while self.parent and self._collection is None:
            self._collection = self.parent.collection
        return self._collection

    @property
    def segments(self):
        cur_delimiter = self.delimiter if self._nested else self.url_delimiter
        if isinstance(self.parent, UrlPath):
            self.parent._nested = True
            return [self._name, cur_delimiter]
        else:
            return [self.url_delimiter, self._name, cur_delimiter]

    @property
    def url_delimiter(self):
        return ":/"
