from office365.runtime.paths.entity import EntityPath
from office365.runtime.paths.resource_path import ResourcePath


class MePath(EntityPath):
    """SignedIn user resource path"""

    def __init__(self):
        super(MePath, self).__init__("me", None, ResourcePath("users"))
