from office365.runtime.paths.resource_path import ResourcePath


class RootResourcePath(ResourcePath):
    """Resource path for OneDrive path-based addressing"""

    def __init__(self, parent):
        super(RootResourcePath, self).__init__("root", parent)


