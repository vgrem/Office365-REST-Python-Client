from office365.runtime.paths.resource_path import ResourcePath


class EntityPath(ResourcePath):
    """Path for addressing a single SharePoint entity"""

    @property
    def segment(self):
        if isinstance(self.key, int):
            return "({0})".format(self.key)
        return "('{0}')".format(self.key)

    @property
    def delimiter(self):
        return None
