from abc import ABCMeta, abstractproperty


class ResourcePath(object):
    """OData resource path"""
    __metaclass__ = ABCMeta

    def __init__(self, context, parent=None):
        self._parent = parent
        self._context = context

    def build_path_url(self):
        current = self
        paths = []
        while current:
            paths.insert(0, current.url)
            current = current._parent
        return '/'.join(paths)

    @abstractproperty
    def url(self):
        return ""
