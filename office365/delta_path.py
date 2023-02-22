from office365.runtime.paths.entity import EntityPath


class DeltaPath(EntityPath):
    """Delta path"""

    def __init__(self, parent=None):
        super(DeltaPath, self).__init__("delta", parent, parent)
