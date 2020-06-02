
class ResourcePath(object):
    """OData resource path"""

    def __init__(self, segment, parent=None):
        self._segment = segment
        self._parent = parent

    def to_url(self):
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

