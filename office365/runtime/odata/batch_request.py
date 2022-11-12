from abc import abstractmethod

from office365.runtime.client_request import ClientRequest


class ODataBatchRequest(ClientRequest):

    @abstractmethod
    def build_request(self, query):
        """
        Builds a request

        :type query: office365.runtime.queries.batch.BatchQuery
        :rtype: office365.runtime.http.request_options.RequestOptions
        """
        pass

    @abstractmethod
    def process_response(self, response, query):
        """
        :type response: requests.Response
        :type query: office365.runtime.queries.batch.BatchQuery
        """
        pass
