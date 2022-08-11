from office365.runtime.paths.resource_path import ResourcePath


class EntityPath(ResourcePath):

    def __init__(self, name=None, parent=None, collection=None):
        """
        :param str or None name:
        :param ResourcePath or None collection:
        """
        super(EntityPath, self).__init__(name, parent)
        self._collection = collection

    @property
    def collection(self):
        return self._collection

    @property
    def segments(self):
        return [self.delimiter, str(self.name or '<id>')]

    def normalize(self, name, inplace=False):
        """
        Normalizes entity path

        :type name: str or None
        :type inplace: bool
        """
        if inplace:
            self._name = name
            self._parent = self.collection
            self.__class__ = ResourcePath
            return self
        else:
            return ResourcePath(name, self.collection)
