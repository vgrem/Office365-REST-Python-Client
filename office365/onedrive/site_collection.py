from office365.runtime.client_value_object import ClientValueObject


class SiteCollection(ClientValueObject):
    """The siteCollection resource provides more information about a site collection. """

    def __init__(self):
        super(SiteCollection, self).__init__()
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
