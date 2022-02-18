from office365.runtime.paths.resource_path import ResourcePath


class EntityResourcePath(ResourcePath):

    @property
    def segments(self):
        return ["(", "'{0}'".format(self._name), ")"]
