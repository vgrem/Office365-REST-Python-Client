import abc
from time import sleep

from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.client_result import ClientResult
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.queries.client_query import ClientQuery
from office365.runtime.queries.read_entity import ReadEntityQuery


class ClientRuntimeContext(object):

    def build_request(self, query):
        """
        Builds a request

        :type query: office365.runtime.queries.client_query.ClientQuery
        """
        return self.pending_request().build_request(query)

    def execute_query_retry(self, max_retry=5, timeout_secs=5, success_callback=None, failure_callback=None,
                            exceptions=(ClientRequestException,)):
        """
        Executes the current set of data retrieval queries and method invocations and retries it if needed.

        :param int max_retry: Number of times to retry the request
        :param int timeout_secs: Seconds to wait before retrying the request.
        :param (office365.runtime.client_object.ClientObject)-> None success_callback:
        :param (int, requests.exceptions.RequestException)-> None failure_callback:
        :param exceptions: tuple of exceptions that we retry
        """

        for retry in range(1, max_retry):
            try:
                self.execute_query()
                if callable(success_callback):
                    success_callback(self.pending_request().current_query.return_type)
                break
            except exceptions as e:
                self.add_query(self.pending_request().current_query)
                if callable(failure_callback):
                    failure_callback(retry, e)
                sleep(timeout_secs)

    @abc.abstractmethod
    def pending_request(self):
        """
        :rtype: office365.runtime.client_request.ClientRequest
        """
        pass

    @abc.abstractmethod
    def service_root_url(self):
        """
        :rtype: str
        """
        pass

    @abc.abstractmethod
    def authenticate_request(self, request):
        """
        :type request: office365.runtime.http.request_options.RequestOptions
        """
        pass

    def load(self, client_object, properties_to_retrieve=None, before_loaded=None, after_loaded=None):
        """Prepare retrieval query

        :type properties_to_retrieve: list[str] or None
        :type client_object: office365.runtime.client_object.ClientObject
        :type before_loaded: (office365.runtime.http.request_options.RequestOptions) -> None
        :type after_loaded: (office365.runtime.client_object.ClientObject) -> None
        """
        qry = ReadEntityQuery(client_object, properties_to_retrieve)
        self.add_query(qry)
        if callable(before_loaded):
            self.before_execute(before_loaded)
        if callable(after_loaded):
            def _action():
                after_loaded(client_object)
            self.after_query_execute(qry, _action)
        return qry

    def before_execute(self, action, once=True, *args, **kwargs):
        """
        Attach an event handler which is triggered before request is submitted to server

        :param (office365.runtime.http.request_options.RequestOptions, any) -> None action:
        :param bool once:
        :return: None
        """

        def _process_request(request):
            if once:
                self.pending_request().beforeExecute -= _process_request
            action(request, *args, **kwargs)

        self.pending_request().beforeExecute += _process_request

    def after_query_execute(self, query, action, *args, **kwargs):
        """
        Attach an event handler which is triggered after query is submitted to server

        :type query: office365.runtime.queries.client_query.ClientQuery
        :type action: (Response, *args, **kwargs) -> None
        :return: None
        """

        def _process_response(resp):
            """
            :type resp: requests.Response
            """
            if self.pending_request().current_query.id == query.id:
                action(*args, **kwargs)
                self.pending_request().afterExecute -= _process_response

        self.pending_request().afterExecute += _process_response

    def after_execute(self, action, once=True, *args, **kwargs):
        """
        Attach an event handler which is triggered after request is submitted to server

        :param (RequestOptions, *args, **kwargs) -> None action:
        :param bool once:
        :return: None
        """

        def _process_response(response):
            if once:
                self.pending_request().afterExecute -= _process_response
            action(response, *args, **kwargs)

        self.pending_request().afterExecute += _process_response

    def execute_request_direct(self, path):
        """
        :type path: str
        """
        full_url = "".join([self.service_root_url(), "/", path])
        request = RequestOptions(full_url)
        return self.pending_request().execute_request_direct(request)

    def execute_query(self):
        """Submit request(s) to the server"""
        self.pending_request().execute_query()

    def add_query(self, query):
        """
        :type query: office365.runtime.queries.client_query.ClientQuery
        """
        self.pending_request().add_query(query)

    def clear(self):
        self.pending_request().clear()

    def get_metadata(self):
        return_type = ClientResult(self)

        def _construct_download_request(request):
            """
            :type request: office365.runtime.http.request_options.RequestOptions
            """
            request.url += "/$metadata"
            request.method = HttpMethod.Get

        def _process_download_response(response):
            """
            :type response: requests.Response
            """
            response.raise_for_status()
            return_type.set_property("__value", response.content)

        qry = ClientQuery(self)
        self.before_execute(_construct_download_request)
        self.after_execute(_process_download_response)
        self.add_query(qry)
        return return_type

