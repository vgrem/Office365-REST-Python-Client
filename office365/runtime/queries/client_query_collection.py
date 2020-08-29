from office365.runtime.queries.client_query import ClientQuery, ReadEntityQuery


class ClientQueryCollection(ClientQuery):
    """Client query collection"""

    def __init__(self, queries=None):
        super().__init__(None)
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
