from office365.runtime.clientValue import ClientValue
from office365.sharepoint.search.queryResult import QueryResult


class SearchResult(ClientValue):

    def __init__(self):
        super().__init__()
        self.PrimaryQueryResult = QueryResult()
        self.ElapsedTime = None
        self.Properties = None
        self.SecondaryQueryResults = None
        self.SpellingSuggestion = None
        self.TriggeredRules = None

    @property
    def entity_type_name(self):
        return "Microsoft.Office.Server.Search.REST.SearchResult"
