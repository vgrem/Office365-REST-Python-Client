from office365.runtime.client_value import ClientValue
from office365.sharepoint.search.query_result import QueryResult


class SearchResult(ClientValue):
    """
    The SearchResult structure resembles the ResultTableCollection structure
    (specified in [MS-QSSWS] section 3.1.4.1.3.1). However, the individual result tables that share the same
    QueryId are grouped together in a QueryResult structure (specified in section 3.1.5.2).
    The search result tables that have exactly the same QueryId value as specified by the protocol client are grouped
    in the same QueryResult structure accessed through the PrimaryQueryResult property. All other QueryResult buckets
    are organized in a CSOM array of QueryResults accessed through the SecondaryQueryResults property.
    """

    def __init__(self, elapsed_time=None, primary_query_result=QueryResult(), properties=None):
        """
        :param str elapsed_time:  The time it took to execute the search query, in milliseconds.
            This element MUST contain a non-negative number.
        :param QueryResult primary_query_result: A grouping of result tables, where each contained result table is a
            ResultTable as specified in [MS-QSSWS] section 3.1.4.1.3.6.
        :param dict properties: Specifies a property bag of key value pairs
        """
        super(SearchResult, self).__init__()
        self.PrimaryQueryResult = primary_query_result
        self.ElapsedTime = elapsed_time
        self.Properties = properties
        self.SecondaryQueryResults = None
        self.SpellingSuggestion = None
        self.TriggeredRules = None

    @property
    def entity_type_name(self):
        return "Microsoft.Office.Server.Search.REST.SearchResult"
