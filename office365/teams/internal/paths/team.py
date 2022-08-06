from office365.runtime.paths.entity import EntityPath
from office365.runtime.paths.resource_path import ResourcePath


class TeamPath(EntityPath):
    """Team container path"""

    def __init__(self, parent=None):
        super(TeamPath, self).__init__("team", parent, ResourcePath("teams"))
