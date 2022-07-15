from office365.runtime.client_value import ClientValue


class QueryContext(ClientValue):
    """This object contains the query context properties."""

    def __init__(self, site_id=None):
        """
        :param str site_id: This property contains the site identification.
        """
        self.SpSiteId = site_id
