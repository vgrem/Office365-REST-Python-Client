from office365.runtime.resource_path import ResourcePath


class ResourcePathUrl(ResourcePath):
    """Resource path for OneDrive path-based addressing"""

    def __init__(self, url, parent):
        super().__init__(url, parent)

    def to_url(self):
        return self._parent.to_url() + f":/{self.segment}:/"
