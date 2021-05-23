import uuid

from office365.runtime.queries.client_query import ClientQuery
from office365.runtime.queries.read_entity_query import ReadEntityQuery


def create_boundary(prefix, compact=False):
    """Creates a string that can be used as a multipart request boundary.

    :param bool compact:
    :param str prefix: String to use as the start of the boundary string
    """
    if compact:
        return prefix + str(uuid.uuid4())[:8]
    else:
        return prefix + str(uuid.uuid4())


class BatchQuery(ClientQuery):
    """Client query collection"""

    def __init__(self, context, queries=None):
        """

        :type context: office365.runtime.client_runtime_context.ClientRuntimeContext
        :type queries: list[]
        """
        super().__init__(context)
        self._current_boundary = create_boundary("batch_")
        if queries is None:
            queries = []
        self._queries = queries

    def add(self, query):
        """

        :type query: ClientQuery
        """
        self._queries.append(query)

    def get(self, index):
        result = [qry for qry in self.change_sets if qry.return_type is not None] + self.get_queries
        return result[index]

    @property
    def current_boundary(self):
        return self._current_boundary

    @property
    def change_sets(self):
        return [qry for qry in self._queries if not isinstance(qry, ReadEntityQuery)]

    @property
    def queries(self):
        """
        :rtype: list[ClientQuery]
        """
        return self._queries

    @property
    def get_queries(self):
        return [qry for qry in self._queries if isinstance(qry, ReadEntityQuery)]

    @property
    def has_change_sets(self):
        return len(self.change_sets) > 0
