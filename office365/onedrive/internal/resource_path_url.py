from office365.runtime.resource_path import ResourcePath


class ResourcePathUrl(ResourcePath):
    """Resource path for OneDrive path-based addressing"""

    def __init__(self, url, parent):
        super(ResourcePathUrl, self).__init__(url, parent)

    @property
    def delimiter(self):
        return ":/"

    @property
    def delimiter_precedence(self):
        return 2

    @property
    def require_closing_delimiter(self):
        return True
