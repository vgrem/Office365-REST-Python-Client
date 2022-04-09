from office365.runtime.paths.resource_path import ResourcePath


class RootPath(ResourcePath):
    """Resource path for OneDrive path-based addressing"""

    def __init__(self, parent):
        super(RootPath, self).__init__("root", parent)

    def normalize(self, name, parent=None, inplace=False):
        if self.parent.name == "drive":
            return super(RootPath, self).normalize(name, ResourcePath("items", self.parent), inplace)
        else:
            return super(RootPath, self).normalize(name, self.parent, inplace)
