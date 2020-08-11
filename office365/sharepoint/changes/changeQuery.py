from office365.runtime.client_value import ClientValue


class ChangeQuery(ClientValue):
    """Defines a query that is performed against the change log."""

    def __init__(self, site=False, web=False, list_=False):
        """

        :param bool site: Gets or sets a value that specifies whether changes to site collections
            are included in the query.
        :param bool web: Gets or sets a value that specifies whether changes to Web sites are included in the query.
        :param bool list_: Gets or sets a value that specifies whether changes to lists are included in the query.
        """
        super().__init__()
        self.Web = web
        self.Site = site
        self.List = list_

    @property
    def entity_type_name(self):
        return 'SP.ChangeQuery'
