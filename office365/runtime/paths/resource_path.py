class ResourcePath(object):
    """OData resource path"""

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
        return [self.delimiter, str(self.name)]

    @property
    def name(self):
        return self._name

    @property
    def delimiter(self):
        return "/"
