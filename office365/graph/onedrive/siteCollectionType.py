from office365.runtime.client_value import ClientValue


class SiteCollectionType(ClientValue):
    """The siteCollection resource provides more information about a site collection. """

    def __init__(self):
        super(SiteCollectionType, self).__init__()
        self._hostname = None
        self._root = None

    @property
    def hostname(self):
        """The hostname for the site collection."""
        return self._hostname

    @property
    def root(self):
        """If present, indicates that this is a root site collection in SharePoint."""
        return self._root
