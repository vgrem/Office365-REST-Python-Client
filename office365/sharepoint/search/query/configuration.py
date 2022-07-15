from office365.runtime.client_value import ClientValue
from office365.sharepoint.search.query.context import QueryContext


class QueryConfiguration(ClientValue):
    """This object contains the query configuration for the local farm and is the response
    to the REST call get query configuration (section 3.1.5.18.2.1.6)."""

    def __init__(self, query_context=QueryContext()):
        """
        :param QueryContext query_context: This property contains the query context.
        """
        self.QueryContext = query_context
