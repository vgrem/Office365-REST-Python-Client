from office365.onedrive.internal.paths.root import RootPath
from office365.runtime.paths.entity import EntityPath


class UrlPath(EntityPath):
    """Resource path for OneDrive entity path-based addressing"""

    def __init__(self, url, parent, collection=None):
        """
        :param str url: File or Folder server relative url
        :type parent: office365.runtime.paths.resource_path.ResourcePath
        """
        if isinstance(parent, UrlPath):
            url = "/".join([parent.key, url])
            collection = parent.collection
            parent = parent.parent
        elif isinstance(parent, RootPath):
            collection = parent.collection
        super(UrlPath, self).__init__(url, parent, collection)

    @property
    def segment(self):
        return ":/{0}:/".format(self._key)

    @property
    def delimiter(self):
        return None
