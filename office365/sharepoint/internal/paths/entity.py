from office365.runtime.paths.resource_path import ResourcePath


class EntityPath(ResourcePath):
    """Path for addressing a single SharePoint entity"""

    @property
    def segments(self):
        if isinstance(self.key, int):
            return ["(", "{0}".format(self.key), ")"]
        return ["(", "'{0}'".format(self.key), ")"]
