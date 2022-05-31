from office365.runtime.client_value import ClientValue


class SiteCollection(ClientValue):
    """The siteCollection resource provides more information about a site collection."""

    def __init__(self, root=None, hostname=None, data_location_code=None):
        """

        :param office365.onedrive.root.Root root: The hostname for the site collection.
        :param str hostname: The hostname for the site collection.
        :param str data_location_code: The geographic region code for where this site collection resides
        """
        super(SiteCollection, self).__init__()
        self.root = root
        self.hostname = hostname
        self.dataLocationCode = data_location_code
