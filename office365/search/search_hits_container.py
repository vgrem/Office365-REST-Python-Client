from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.search.search_hit import SearchHit


class SearchHitsContainer(ClientValue):

    def __init__(self, hits=None, more_results_available=None, total=None):
        super(SearchHitsContainer, self).__init__()
        if hits is None:
            hits = ClientValueCollection(SearchHit)
        self.hits = hits
        self.moreResultsAvailable = more_results_available
        self.total = total
