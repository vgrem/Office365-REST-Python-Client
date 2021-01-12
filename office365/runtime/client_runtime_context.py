import abc
from time import sleep

from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.queries.read_entity_query import ReadEntityQuery


class ClientRuntimeContext(object):

    def __init__(self):
        """
        Client runtime context
        """

    @property
    def current_query(self):
        return self.pending_request().current_query

    def execute_query_retry(self, max_retry=5, timeout_secs=5, success_callback=None, failure_callback=None):
        """
        Executes the current set of data retrieval queries and method invocations and retries it if needed.

        :param int max_retry: Number of times to retry the request
        :param int timeout_secs: Seconds to wait before retrying the request.
        :param (ClientObject)-> None success_callback:
        :param (int)-> None failure_callback:
        """

        for retry in range(1, max_retry):
            try:
                self.execute_query()
                if callable(success_callback):
                    success_callback(self.pending_request().current_query.return_type)
                break
            except ClientRequestException:
                self.add_query(self.pending_request().current_query, True)
                sleep(timeout_secs)
                if callable(failure_callback):
                    failure_callback(retry)

    @abc.abstractmethod
    def pending_request(self):
        """
        :rtype: office365.runtime.client_request.ClientRequest
        """
        pass

    @abc.abstractmethod
    def service_root_url(self):
        pass

    @abc.abstractmethod
    def authenticate_request(self, request):
        """
        :type request: office365.runtime.http.request_options.RequestOptions
        """
        pass

    def build_request(self):
        return self.pending_request().build_request()

    def load(self, client_object, properties_to_retrieve=None):
        """Prepare retrieval query

        :type properties_to_retrieve: list[str] or None
        :type client_object: office365.runtime.client_object.ClientObject
        """
        qry = ReadEntityQuery(client_object, properties_to_retrieve)
        self.pending_request().add_query(qry)
        return qry

    def before_execute(self, action, once=True):
        """
        Attach an event handler which is triggered before request is submitted to server

        :param (RequestOptions) -> None action:
        :param bool once:
        :return: None
        """
        def _process_request(request):
            if once:
                self.pending_request().beforeExecute -= _process_request
            action(request)
        self.pending_request().beforeExecute += _process_request

    def before_execute_query(self, action):
        """
        Attach an event handler which is triggered before query is submitted to server

        :param (RequestOptions) -> None action:
        :return: None
        """
        def _prepare_request(request):
            qry = self.pending_request().current_query
            action(qry)
        self.pending_request().beforeExecute += _prepare_request

    def after_execute_query(self, action):
        """
        Attach an event handler which is triggered after query is submitted to server

        :param (RequestOptions) -> None action:
        :return: None
        """
        def _process_response(response):
            qry = self.pending_request().current_query
            action(qry)
        self.pending_request().afterExecute += _process_response

    def after_execute(self, action, once=True):
        """
        Attach an event handler which is triggered after request is submitted to server

        :param (RequestOptions) -> None action:
        :param bool once:
        :return: None
        """

        def _process_response(response):
            if once:
                self.pending_request().afterExecute -= _process_response
            action(response)

        self.pending_request().afterExecute += _process_response

    def execute_request_direct(self, request):
        """
        :type request: RequestOptions
        """
        return self.pending_request().execute_request_direct(request)

    def execute_query(self):
        self.pending_request().execute_query()

    def add_query(self, query, to_begin=False):
        """
        Adds query to internal queue

        :type to_begin: bool
        :type query: ClientQuery
        """
        self.pending_request().add_query(query, to_begin)

    def remove_query(self, query):
        self.pending_request().remove_query(query)

    def clear_queries(self):
        self.pending_request().queries.clear()
