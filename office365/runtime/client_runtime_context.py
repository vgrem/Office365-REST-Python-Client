import abc
from time import sleep
from typing import TypeVar

from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.client_result import ClientResult
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.queries.client_query import ClientQuery
from office365.runtime.queries.read_entity import ReadEntityQuery

T = TypeVar('T', bound='ClientObject')


class ClientRuntimeContext(object):

    def __init__(self):
        self._queries = []
        self._current_query = None

    @property
    def current_query(self):
        """
        :rtype: office365.runtime.queries.client_query.ClientQuery
        """
        return self._current_query

    @property
    def has_pending_request(self):
        return len(self._queries) > 0

    def build_request(self, query):
        """
        Builds a request

        :type query: office365.runtime.queries.client_query.ClientQuery
        """
        self._current_query = query
        return self.pending_request().build_custom_request(query)

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

        for retry in range(1, max_retry + 1):
            try:
                self.execute_query()
                if callable(success_callback):
                    success_callback(self.current_query.return_type)
                break
            except exceptions as e:
                self.add_query(self.current_query)
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

    def load(self, client_object, properties_to_retrieve=None, before_loaded=None, after_loaded=None):
        """Prepare retrieval query

        :type properties_to_retrieve: list[str] or None
        :type client_object: office365.runtime.client_object.ClientObject
        :type before_loaded: (office365.runtime.http.request_options.RequestOptions) -> None
        :type after_loaded: (T) -> None
        """
        qry = ReadEntityQuery(client_object, properties_to_retrieve)
        self.add_query(qry)
        if callable(before_loaded):
            self.before_execute(before_loaded)
        if callable(after_loaded):
            self.after_query_execute(after_loaded, client_object)
        return self

    def before_query_execute(self, action, once=True, *args, **kwargs):
        """
        Attach an event handler which is triggered before query is submitted to server

        :type action: (office365.runtime.http.request_options.RequestOptions, *args, **kwargs) -> None
        :param bool once: Flag which determines whether action is executed once or multiple times
        """

        query = self._queries[-1]

        def _prepare_request(request):
            """
            :type request: office365.runtime.http.request_options.RequestOptions
            """

            if self.current_query.id == query.id:
                if once:
                    self.pending_request().beforeExecute -= _prepare_request
                action(request, *args, **kwargs)

        self.pending_request().beforeExecute += _prepare_request
        return self

    def before_execute(self, action, once=True, *args, **kwargs):
        """
        Attach an event handler which is triggered before request is submitted to server

        :param (office365.runtime.http.request_options.RequestOptions, any) -> None action:
        :param bool once: Flag which determines whether action is executed once or multiple times
        """

        def _process_request(request):
            if once:
                self.pending_request().beforeExecute -= _process_request
            action(request, *args, **kwargs)

        self.pending_request().beforeExecute += _process_request
        return self

    def after_query_execute(self, action, *args, **kwargs):
        """
        Attach an event handler which is triggered after query is submitted to server

        :type action: (Response, *args, **kwargs) -> None
        """
        query = self._queries[-1]

        def _process_response(resp):
            """
            :type resp: requests.Response
            """
            resp.raise_for_status()
            if self.current_query.id == query.id:
                self.pending_request().afterExecute -= _process_response
                action(*args, **kwargs)

        self.pending_request().afterExecute += _process_response

        execute_first = kwargs.pop("execute_first", False)
        if execute_first and len(self._queries) > 1:
            self._queries.insert(0, self._queries.pop())

        return self

    def after_execute(self, action, once=True, *args, **kwargs):
        """
        Attach an event handler which is triggered after request is submitted to server

        :param (RequestOptions, *args, **kwargs) -> None action:
        :param bool once:
        """

        def _process_response(response):
            if once:
                self.pending_request().afterExecute -= _process_response
            action(response, *args, **kwargs)

        self.pending_request().afterExecute += _process_response
        return self

    def execute_request_direct(self, path):
        """
        :type path: str
        """
        full_url = "".join([self.service_root_url(), "/", path])
        request = RequestOptions(full_url)
        return self.pending_request().execute_request_direct(request)

    def execute_query(self):
        """Submit request(s) to the server"""
        while self.has_pending_request:
            qry = self._get_next_query()
            self.pending_request().execute_query(qry)

    def add_query(self, query):
        """
        :type query: office365.runtime.queries.client_query.ClientQuery
        """
        self._queries.append(query)
        return self

    def clear(self):
        self._current_query = None
        self._queries = []
        return self

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

    def _get_next_query(self, count=1):
        """
        :type count: int
        """
        if count == 1:
            qry = self._queries.pop(0)
        else:
            from office365.runtime.queries.batch import BatchQuery
            qry = BatchQuery(self)
            while self.has_pending_request and count > 0:
                qry.add(self._queries.pop(0))
                count = count - 1
        self._current_query = qry
        return qry
