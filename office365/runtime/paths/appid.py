from office365.runtime.paths.resource_path import ResourcePath


class AppIdPath(ResourcePath):
    """Path for addressing a Service Principal"""

    @property
    def segment(self):
        return "(appId='{0}')".format(self.key)

    @property
    def delimiter(self):
        return None
