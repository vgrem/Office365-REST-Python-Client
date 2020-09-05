import uuid

from office365.runtime.queries.client_query import ClientQuery
from office365.runtime.queries.create_entity_query import CreateEntityQuery
from office365.runtime.queries.read_entity_query import ReadEntityQuery
from office365.runtime.queries.service_operation_query import ServiceOperationQuery


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
        result = [qry for qry in self._queries
                  if isinstance(qry, ReadEntityQuery)
                  or isinstance(qry, CreateEntityQuery)
                  or isinstance(qry, ServiceOperationQuery)]
        return result[index]

    @property
    def current_boundary(self):
        return self._current_boundary

    @property
    def change_sets(self):
        return [qry for qry in self._queries if not isinstance(qry, ReadEntityQuery)]

    @property
    def has_change_sets(self):
        return len(self.change_sets) > 0

    def next_get_query(self):
        for qry in self._queries:
            if isinstance(qry, ReadEntityQuery):
                self.context.pending_request()._current_query = qry
                yield qry

    def next_change_set(self):
        for qry in self.change_sets:
            self.context.pending_request()._current_query = qry
            yield qry
