from office365.runtime.paths.resource_path import ResourcePath


class UrlPath(ResourcePath):
    """Resource path for OneDrive path-based addressing"""

    def __init__(self, rel_url, parent):
        """
        :param str rel_url: File or Folder relative url
        :type parent: office365.runtime.paths.ResourcePath
        """
        super(UrlPath, self).__init__(rel_url, parent)
        self._nested = False

    def normalize(self, value, parent=None, inplace=False):
        path = self.parent.normalize(value)
        return super(UrlPath, self).normalize(path.name, path.parent, inplace)

    @property
    def segments(self):
        cur_delimiter = "/" if self._nested else self.delimiter
        if isinstance(self.parent, UrlPath):
            self.parent._nested = True
            return [self._name, cur_delimiter]
        else:
            return [self.delimiter, self._name, cur_delimiter]

    @property
    def delimiter(self):
        return ":/"
