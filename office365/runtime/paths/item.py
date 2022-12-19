from office365.runtime.paths.entity import EntityPath


class ItemPath(EntityPath):

    def __init__(self, parent=None):
        super(ItemPath, self).__init__(None, parent, parent)
