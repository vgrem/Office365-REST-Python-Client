
class ResourcePath(object):
    """OData resource path"""

    def __init__(self, segment, parent=None):
        """

        :type segment: str
        :type parent: ResourcePath or None
        """
        self._segment = segment
        self._parent = parent

    def to_url(self):
        """
        Builds url
        :rtype: str
        """
        delimiter = '/'
        current = self
        segments = []
        while current:
            segments.insert(0, current.segment)
            current = current.parent
        return delimiter.join(segments)

    @property
    def parent(self):
        return self._parent

    @property
    def segment(self):
        return self._segment
