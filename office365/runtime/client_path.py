from abc import ABCMeta


class ClientPath(object):
    __metaclass__ = ABCMeta

    def __init__(self, parent=None):
        """
        :type parent: ClientPath or None
        """
        self._parent = parent

    def __repr__(self):
        return self.to_url()

    def __str__(self):
        return self.to_url()

    def to_url(self):
        """
        Builds url

        :rtype: str
        """
        current = self
        all_segments = []
        while current:
            all_segments = current.segments + all_segments
            current = current.parent
        return "".join(all_segments)

    @property
    def parent(self):
        """
        :rtype: ClientPath or None
        """
        return self._parent

    @property
    def segments(self):
        return []

    @property
    def name(self):
        return self.segments[-1] if len(self.segments) > 0 else ""

    @property
    def delimiter(self):
        return "/"
