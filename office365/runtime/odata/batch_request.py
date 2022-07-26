from abc import abstractmethod

from office365.runtime.client_request import ClientRequest
from office365.runtime.queries.batch import BatchQuery


class ODataBatchRequest(ClientRequest):

    def __init__(self, context, items_per_batch):
        super(ODataBatchRequest, self).__init__(context)
        self.items_per_batch = items_per_batch

    def add_query(self, query):
        if isinstance(query, BatchQuery):
            super(ODataBatchRequest, self).add_query(query)
        else:
            if self._current_query is None or len(self.current_query.queries) == self.items_per_batch:
                super(ODataBatchRequest, self).add_query(BatchQuery(self.context, [query]))
            else:
                self.current_query.add(query)  # Aggregate requests into batch request
        return self

    @abstractmethod
    def build_request(self, query):
        """
        Builds a request

        :type query: office365.runtime.queries.client_query.ClientQuery
        :rtype: office365.runtime.http.request_options.RequestOptions
        """
        pass

    @abstractmethod
    def process_response(self, response):
        """
        :type response: requests.Response
        """
        pass

    @property
    def current_query(self):
        """
        :rtype: office365.runtime.queries.batch.BatchQuery
        """
        return self._current_query
