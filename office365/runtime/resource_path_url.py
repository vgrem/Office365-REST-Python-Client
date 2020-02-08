from office365.runtime.resource_path import ResourcePath


class ResourcePathUrl(ResourcePath):
    """Resource path for OneDrive path-based addressing"""

    def __init__(self, context, parent, url):
        super(ResourcePathUrl, self).__init__(context, parent)
        self._url = url

    def to_string(self):
        return self._parent.to_string() + self.segment

    @property
    def segment(self):
        return ":/{0}:/".format(self._url)
