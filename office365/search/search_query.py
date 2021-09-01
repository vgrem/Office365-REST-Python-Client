from office365.runtime.client_value import ClientValue


class SearchQuery(ClientValue):

    def __init__(self, query_string=None):
        super(SearchQuery, self).__init__()
        self.queryString = query_string
