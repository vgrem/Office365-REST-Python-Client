from office365.runtime.paths.entity import EntityPath


class NonePath(EntityPath):

    def __init__(self, parent=None):
        super(NonePath, self).__init__(None, parent, parent)

