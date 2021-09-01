from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.search.search_hits_container import SearchHitsContainer


class SearchResponse(ClientValue):
    """Represents results from a search query, and the terms used for the query."""

    def __init__(self, search_terms=None, hits_containers=None):
        """

        """
        super(SearchResponse, self).__init__()
        self.searchTerms = search_terms
        if hits_containers is None:
            hits_containers = ClientValueCollection(SearchHitsContainer)
        self.hitsContainers = hits_containers
