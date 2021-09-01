from office365.runtime.client_value import ClientValue


class SearchRequest(ClientValue):
    """A search request formatted in a JSON blob."""

    def __init__(self, query, entity_types=None):
        """
        :type query: office365.search.search_query.SearchQuery
        :type entity_types: list[str]
        """
        super(SearchRequest, self).__init__()
        self.query = query
        self.entityTypes = entity_types
