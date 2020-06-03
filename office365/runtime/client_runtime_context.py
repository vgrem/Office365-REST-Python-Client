import abc
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.client_request import ClientRequest
from office365.runtime.client_query import ReadEntityQuery
from office365.runtime.utilities.EventHandler import EventHandler
from office365.runtime.client_query import ClientQuery
from office365.runtime.auth.authentication_context import AuthenticationContext


class ClientRuntimeContext(object):

    def __init__(self, url, auth_context=None):
        """
        Client runtime context for services

        :type url: str
        :type auth_context: AuthenticationContext or None
        """
        self.__service_root_url = url
        self.__auth_context = auth_context
        self.afterExecuteOnce = EventHandler(True)

    @abc.abstractmethod
    def get_pending_request(self):
        """
        :rtype: ClientRequest

        """
        pass

    @property
    def has_pending_request(self):
        return len(self.get_pending_request().queries) > 0

    def authenticate_request(self, request):
        self.__auth_context.authenticate_request(request)

    def load(self, client_object, properties_to_retrieve=None):
        """Prepare query

        :type properties_to_retrieve: list[str] or None
        :type client_object: office365.runtime.client_object.ClientObject
        """
        qry = ReadEntityQuery(client_object, properties_to_retrieve)
        self.get_pending_request().add_query(qry)

    def execute_request_direct(self, request):
        """

        :type request: RequestOptions
        """
        return self.get_pending_request().execute_request_direct(request)

    def execute_query(self):
        while self.has_pending_request:
            self.get_pending_request().execute_query()
            query = self.get_pending_request().current_query
            self.afterExecuteOnce.notify(query.return_type)

    def add_query(self, query):
        """
        Adds query to internal queue
        :type query: ClientQuery
        """
        self.get_pending_request().add_query(query)

    @property
    def service_root_url(self):
        return self.__service_root_url
