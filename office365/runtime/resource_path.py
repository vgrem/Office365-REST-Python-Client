from abc import ABCMeta, abstractproperty


class ResourcePath(object):
    """OData resource path"""
    __metaclass__ = ABCMeta

    def __init__(self, context, parent=None):
        self._parent = parent
        self._context = context

    def build_url(self):
        delimiter = '/'
        current = self
        segments = []
        while current:
            segments.insert(0, current.segment)
            current = current._parent
        return delimiter.join(segments)

    @property
    def parent(self):
        return self._parent

    @abstractproperty
    def segment(self):
        return ""
