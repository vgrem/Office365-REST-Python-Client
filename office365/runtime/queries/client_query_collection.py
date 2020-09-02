from office365.runtime.queries.client_query import ClientQuery
from office365.runtime.queries.read_entity_query import ReadEntityQuery


class ClientQueryCollection(ClientQuery):
    """Client query collection"""

    def __init__(self, context, queries=None):
        """

        :type context: office365.runtime.client_runtime_context.ClientRuntimeContext
        :type queries: list[]
        """
        super().__init__(context)
        if queries is None:
            queries = []
        self._queries = queries

    def add(self, query):
        """

        :type query: ClientQuery
        """
        self._queries.append(query)

    @property
    def queries(self):
        return [qry for qry in self._queries if isinstance(qry, ReadEntityQuery)]

    @property
    def change_sets(self):
        return [qry for qry in self._queries if not isinstance(qry, ReadEntityQuery)]
