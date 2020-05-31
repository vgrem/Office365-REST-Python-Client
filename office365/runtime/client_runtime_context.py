import abc
from office365.runtime.client_query import ReadEntityQuery
from office365.runtime.utilities.EventHandler import EventHandler


class ClientRuntimeContext(object):

    def __init__(self, url, auth_context):
        """
        Client runtime context for services
        :type url: str
        :type auth_context: AuthenticationContext
        """
        self.__service_root_url = url
        self.__auth_context = auth_context
        self.afterExecuteOnce = EventHandler(True)

    @abc.abstractmethod
    def get_pending_request(self):
        pass

    @property
    def has_pending_request(self):
        return len(self.get_pending_request().queries) > 0

    def authenticate_request(self, request):
        self.__auth_context.authenticate_request(request)

    def load(self, client_object, properties_to_retrieve=None):
        """Prepare query"""
        qry = ReadEntityQuery(client_object, properties_to_retrieve)
        self.get_pending_request().add_query(qry)

    def execute_request_direct(self, request):
        return self.get_pending_request().execute_request_direct(request)

    def execute_query(self):
        while self.has_pending_request:
            self.get_pending_request().execute_query()
            query = self.get_pending_request().current_query
            self.afterExecuteOnce.notify(query.return_type)

    def add_query(self, query):
        self.get_pending_request().add_query(query)

    @property
    def service_root_url(self):
        return self.__service_root_url
