from office365.runtime.paths.resource_path import ResourcePath


class KeyPath(ResourcePath):
    """Path for addressing a single entity by key"""

    @property
    def segment(self):
        if self.key is None:
            return "(<key>)"
        elif isinstance(self.key, int):
            return "({0})".format(self.key)
        return "('{0}')".format(self.key)

    @property
    def delimiter(self):
        return None
