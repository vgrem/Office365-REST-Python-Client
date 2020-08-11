import abc
from time import sleep

from office365.runtime.client_query import ReadEntityQuery
from office365.runtime.client_request_exception import ClientRequestException


class ClientRuntimeContext(object):

    def __init__(self, service_root_url, auth_context=None):
        """
        Client runtime context for services

        :type service_root_url: str
        :type auth_context: AuthenticationContext or None
        """
        self._service_root_url = service_root_url
        self._auth_context = auth_context
        self._current_query = None

    def execute_query_retry(self, max_retry=5, timeout_secs=5, on_success=None, on_failure=None):
        """
        Executes the current set of data retrieval queries and method invocations and retries it if needed.

        :param int max_retry: Number of times to retry the request
        :param int timeout_secs: Seconds to wait before retrying the request.
        :param (ClientObject)-> None on_success:
        :param (int)-> None on_failure:
        """

        for retry in range(1, max_retry):
            try:
                self.execute_query()
                if callable(on_success):
                    on_success(self.current_query.return_type)
                break
            except ClientRequestException:
                self.add_query(self.current_query, True)
                sleep(timeout_secs)
                if callable(on_failure):
                    on_failure(retry)

    @property
    def current_query(self):
        """
        :rtype: ClientQuery
        """
        return self._current_query

    @abc.abstractmethod
    def get_pending_request(self):
        """
        :rtype: office365.runtime.client_request.ClientRequest
        """
        pass

    @property
    def has_pending_request(self):
        return len(self.get_pending_request().queries) > 0

    def get_next_query(self):
        for qry in self.get_pending_request():
            self._current_query = qry
            yield qry

    def build_request(self):
        return self.get_pending_request().build_request()

    def authenticate_request(self, request):
        self._auth_context.authenticate_request(request)

    def load(self, client_object, properties_to_retrieve=None, on_loaded=None):
        """Prepare query

        :type on_loaded: () -> None
        :type properties_to_retrieve: list[str] or None
        :type client_object: office365.runtime.client_object.ClientObject
        """
        qry = ReadEntityQuery(client_object, properties_to_retrieve)
        self.get_pending_request().add_query(qry)

        def _process_response(resp):
            if self.current_query.id == qry.id:
                self.get_pending_request().afterExecute -= _process_response
                on_loaded()
        if callable(on_loaded):
            self.get_pending_request().afterExecute += _process_response

    def before_execute(self, action, once=True):
        """
        Attach an event handler which is triggered before request is submitted to server

        :param (RequestOptions) -> None action:
        :param bool once:
        :return: None
        """
        def _process_request(request):
            if once:
                self.get_pending_request().beforeExecute -= _process_request
            action(request)
        self.get_pending_request().beforeExecute += _process_request

    def before_execute_query(self, action, target_query=None):
        """
        Attach an event handler which is triggered before request is submitted to server

        :param office365.runtime.client_query.ClientQuery target_query:
        :param (RequestOptions) -> None action:
        :return: None
        """
        def _process_request(request):
            if self.current_query.id == target_query.id:
                action(request)
        self.get_pending_request().beforeExecute += _process_request

    def after_execute(self, action, once=True):
        """
        Attach an event handler which is triggered after request is submitted to server

        :param (RequestOptions) -> None action:
        :param bool once:
        :return: None
        """

        def _process_response(response):
            if once:
                self.get_pending_request().afterExecute -= _process_response
            action(response)

        self.get_pending_request().afterExecute += _process_response

    def execute_request_direct(self, request):
        """
        :type request: RequestOptions
        """
        return self.get_pending_request().execute_request_direct(request)

    def execute_query(self):
        for qry in self.get_pending_request():
            self._current_query = qry
            self.get_pending_request().execute_query()

    def add_query(self, query, to_begin=False):
        """
        Adds query to internal queue

        :type to_begin: bool
        :type query: ClientQuery
        """
        self.get_pending_request().add_query(query, to_begin)

    def clear_queries(self):
        self.get_pending_request().queries.clear()

    @property
    def service_root_url(self):
        return self._service_root_url
