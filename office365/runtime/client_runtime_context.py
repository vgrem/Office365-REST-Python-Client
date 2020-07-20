import abc

from office365.runtime.client_query import ReadEntityQuery


class ClientRuntimeContext(object):

    def __init__(self, service_root_url, auth_context=None):
        """
        Client runtime context for services

        :type service_root_url: str
        :type auth_context: AuthenticationContext or None
        """
        self._service_root_url = service_root_url
        self._auth_context = auth_context

    @abc.abstractmethod
    def get_pending_request(self):
        """
        :rtype: office365.runtime.client_request.ClientRequest
        """
        pass

    @property
    def has_pending_request(self):
        return len(self.get_pending_request().queries) > 0

    def authenticate_request(self, request):
        self._auth_context.authenticate_request(request)

    def load(self, client_object, properties_to_retrieve=None, onLoaded=None):
        """Prepare query

        :type onLoaded: () -> None
        :type properties_to_retrieve: list[str] or None
        :type client_object: office365.runtime.client_object.ClientObject
        """
        qry = ReadEntityQuery(client_object, properties_to_retrieve)
        self.get_pending_request().add_query(qry)

        def _process_response(resp):
            if self.get_pending_request().current_query.id == qry.id:
                self.get_pending_request().afterExecute -= _process_response
                onLoaded()
        if callable(onLoaded):
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
        while self.has_pending_request:
            self.get_pending_request().execute_query()

    def add_query(self, query):
        """
        Adds query to internal queue
        :type query: ClientQuery
        """
        self.get_pending_request().add_query(query)

    def clear_queries(self):
        self.get_pending_request().queries.clear()

    @property
    def service_root_url(self):
        return self._service_root_url
