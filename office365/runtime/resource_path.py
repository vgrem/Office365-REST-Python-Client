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
        current = self
        segments = []
        if self.require_closing_delimiter:
            segments.insert(0, current.delimiter)

        while current:
            segments.insert(0, current.segment)
            if current.parent:
                if current.delimiter_precedence == current.parent.delimiter_precedence:
                    segments.insert(0, "/")
                elif current.delimiter_precedence < current.parent.delimiter_precedence:
                    segments.insert(0, current.parent.delimiter)
                else:
                    segments.insert(0, current.delimiter)
            else:
                segments.insert(0, current.delimiter)
            current = current.parent
        return "".join(segments)

    @property
    def parent(self):
        return self._parent

    @property
    def segment(self):
        return self._segment

    @property
    def delimiter(self):
        return "/"

    @property
    def delimiter_precedence(self):
        return 1

    @property
    def require_closing_delimiter(self):
        return False
