from office365.runtime.paths.v4.entity import EntityPath


class ItemPath(EntityPath):
    """ """

    def __init__(self, parent=None):
        super(ItemPath, self).__init__(None, parent, parent)
