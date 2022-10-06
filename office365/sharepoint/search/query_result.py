from office365.runtime.client_value import ClientValue
from office365.sharepoint.search.refinement_results import RefinementResults


class QueryResult(ClientValue):
    """
    The QueryResult type is a grouping of result tables, where each contained result table is a ResultTable
    as specified in [MS-QSSWS] section 3.1.4.1.3.6.
    """

    def __init__(self, query_id=None):
        """
        :param str query_id: Specifies the identifier for the search query
        """
        self.QueryId = query_id
        self.RefinementResults = RefinementResults()

    @property
    def entity_type_name(self):
        return "Microsoft.Office.Server.Search.REST.QueryResult"
