from office365.runtime.client_value import ClientValue


class SearchQuery(ClientValue):

    def __init__(self, query_string=None):
        """
        Represents a search query that contains search terms and optional filters.

        :param str query_string: The search query containing the search terms.
        """
        super(SearchQuery, self).__init__()
        self.queryString = query_string
