from office365.runtime.paths.resource_path import ResourcePath


class ChildrenResourcePath(ResourcePath):
    """Resource path for OneDrive children addressing"""

    def __init__(self, parent):
        super(ChildrenResourcePath, self).__init__("children", parent)
