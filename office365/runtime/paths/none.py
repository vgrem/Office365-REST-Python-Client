from office365.runtime.paths.resource_path import ResourcePath


class NonePath(ResourcePath):

    def __init__(self, parent=None):
        super(NonePath, self).__init__(None, parent)


