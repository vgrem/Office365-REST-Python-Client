class ResourcePath(object):
    """OData resource path"""

    def __init__(self, key, parent=None):
        """
        :type key: int or str
        :type parent: ResourcePath or None
        """
        self._key = key
        self._parent = parent

    def patch(self, key, inplace=False):
        return self

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
            segments.insert(0, path.segment)
            if path.delimiter:
                segments.insert(0, path.delimiter)
        return "".join(segments)

    @property
    def parent(self):
        return self._parent

    @property
    def segment(self):
        return str(self.key)

    @property
    def key(self):
        return self._key

    @property
    def delimiter(self):
        return "/"
