import abc

from office365.runtime.client_query import ReadEntityQuery
from office365.runtime.utilities.EventHandler import EventHandler


class ClientRuntimeContext(object):
    """Client context"""

    def __init__(self, url, auth_context):
        self.__service_root_url = url
        self.__auth_context = auth_context
        self.afterExecuteOnce = EventHandler()

    @abc.abstractmethod
    def get_pending_request(self):
        pass

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
        while self.has_pending_request():
            self.get_pending_request().execute_query()

    def add_query(self, query):
        self.get_pending_request().add_query(query)

    def _process_specific_response(self, response):
        self.get_pending_request().afterExecute -= self._process_specific_response
        query = self.get_pending_request().current_query
        self.afterExecuteOnce.notify(query.returnType)

    @property
    def serviceRootUrl(self):
        return self.__service_root_url
