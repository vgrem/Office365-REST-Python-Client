from office365.runtime.paths.resource_path import ResourcePath


class EntityPath(ResourcePath):

    def __init__(self, key=None, parent=None, collection=None):
        """
        :param str or None key: Entity key
        :param ResourcePath or None collection:
        """
        super(EntityPath, self).__init__(key, parent)
        self._collection = collection

    @property
    def collection(self):
        return self._collection

    @property
    def segment(self):
        return str(self.key or '<key>')

    def patch(self, key, inplace=False):
        """
        Patches path

        :type key: str or None
        :type inplace: bool
        """
        if inplace:
            self._key = key
            self._parent = self.collection
            self.__class__ = ResourcePath
            return self
        else:
            return ResourcePath(key, self.collection)
