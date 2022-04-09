from office365.runtime.paths.resource_path import ResourcePath


class TeamPath(ResourcePath):

    def __init__(self, parent=None):
        super(TeamPath, self).__init__("team", parent)

    def normalize(self, name, parent=None, inplace=False):
        super(TeamPath, self).normalize(name, ResourcePath("teams"), inplace)
