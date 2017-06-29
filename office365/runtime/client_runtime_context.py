from office365.runtime.action_type import ActionType
from office365.runtime.client_query import ClientQuery
from office365.runtime.client_request import ClientRequest


class ClientRuntimeContext(object):
    """SharePoint client context"""

    def __init__(self, url, auth_context):
        self.__service_root_url = url
        self.__auth_context = auth_context
        self.__pending_request = None
        self.json_format = None

    def authenticate_request(self, request):
        self.__auth_context.authenticate_request(request)

    @property
    def pending_request(self):
        if not self.__pending_request:
            self.__pending_request = ClientRequest(self)
        return self.__pending_request

    def load(self, client_object, properties_to_retrieve=[]):
        """Prepare query"""
        qry = ClientQuery(client_object.url, ActionType.ReadEntry)
        self.pending_request.add_query(qry, client_object)

    def execute_query_direct(self, request):
        return self.pending_request.execute_query_direct(request)

    def execute_query(self):
        self.pending_request.execute_query()

    def add_query(self, query, result_object=None):
        self.pending_request.add_query(query, result_object)

    @property
    def service_root_url(self):
        return self.__service_root_url

