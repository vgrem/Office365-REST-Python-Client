import abc
from time import sleep

from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.client_result import ClientResult
from office365.runtime.compat import is_absolute_url
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.queries.client_query import ClientQuery
from office365.runtime.queries.read_entity_query import ReadEntityQuery


class ClientRuntimeContext(object):

    def build_request(self, query):
        """
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
                    success_callback(self.current_query.return_type)
                break
            except exceptions as e:
                self.add_query(self.current_query, True)
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

    def load(self, client_object, properties_to_retrieve=None):
        """Prepare retrieval query

        :type properties_to_retrieve: list[str] or None
        :type client_object: office365.runtime.client_object.ClientObject
        """
        qry = ReadEntityQuery(client_object, properties_to_retrieve)
        self.add_query(qry)
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
            if self.current_query.id == query.id:
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

    def execute_request_direct(self, request):
        """
        :type request: office365.runtime.http.request_options.RequestOptions or str
        """
        return self.pending_request().execute_request_direct(self._normalize_request(request))

    def execute_query(self):
        self.pending_request().execute_query()

    def add_query(self, query, execute_first=False, set_as_current=True):
        """
        :type query: office365.runtime.queries.client_query.ClientQuery
        :type execute_first: bool
        :type set_as_current: bool
        """
        self.pending_request().add_query(query, execute_first, set_as_current)

    def clear(self):
        self.pending_request().clear()

    def get_metadata(self):
        result = ClientResult(self)

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
            result.value = response.content

        qry = ClientQuery(self)
        self.before_execute(_construct_download_request)
        self.after_execute(_process_download_response)
        self.add_query(qry)
        return result

    @property
    def current_query(self):
        """
        :rtype: office365.runtime.queries.client_query.ClientQuery
        """
        return self.pending_request().current_query

    def _normalize_request(self, request):
        """
        :type request: office365.runtime.http.request_options.RequestOptions or str
        """
        if not isinstance(request, RequestOptions):
            request = RequestOptions(request)

        if not is_absolute_url(request.url):
            url_parts = [self.service_root_url()]
            if not request.url.startswith("/"):
                url_parts.append("/")
            url_parts.append(request.url)
            request.url = "".join(url_parts)
        return request
