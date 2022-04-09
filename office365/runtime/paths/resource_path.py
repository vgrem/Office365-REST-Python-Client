class ResourcePath(object):

    def __init__(self, name, parent=None):
        """
        :type name: str
        :type parent: ResourcePath or None
        """
        self._name = name
        self._parent = parent

    def __iter__(self):
        current = self
        while current:
            yield current
            current = current.parent

    def __repr__(self):
        return self.to_url()

    def __str__(self):
        return self.to_url()

    def normalize(self, name, parent=None, inplace=False):
        """
        :type name: str or None
        :type parent: ResourcePath or None
        :type inplace: bool
        """
        if parent is None:
            parent = self.parent

        if inplace:
            self._name = name
            self._parent = parent
            self.__class__ = ResourcePath
            return self
        else:
            return ResourcePath(name, parent)

    def to_url(self):
        """
        Builds url

        :rtype: str
        """
        segments = []
        for path in self:
            segments = path.segments + segments
        return "".join(segments)

    @property
    def parent(self):
        return self._parent

    @property
    def segments(self):
        return [self.delimiter, str(self._name or '')]

    @property
    def name(self):
        return self._name

    @property
    def delimiter(self):
        return "/"
