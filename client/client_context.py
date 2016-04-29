from site import Site
from web import Web
from client.client_object import ClientObject
from client.runtime.client_action_type import ClientActionType
from client.runtime.client_query import ClientQuery
from client.runtime.client_request import ClientRequest


class ClientContext(object):
    """SharePoint client context"""

    def __init__(self, url, auth_context):
        self.__base_url = url
        self.__auth_context = auth_context
        self.__web = None
        self.__site = None
        self.__pending_request = None
        self.__queries = []

    @property
    def web(self):
        """Get Web client object"""
        if not self.__web:
            self.__web = Web(self)
        return self.__web

    @property
    def site(self):
        """Get Site client object"""
        if not self.__site:
            self.__site = Site(self)
        return self.__site

    @property
    def pending_request(self):
        if not self.__pending_request:
            self.__pending_request = ClientRequest(self.__base_url, self.__auth_context)
        return self.__pending_request

    def load(self, client_object):
        """Prepare query for the server"""
        qry = ClientQuery(client_object.url, ClientActionType.Read)
        qry.add_result_object(client_object)
        self.add_query(qry)

    def execute_query(self):
        """Submit pending request to the server"""
        for qry in self.__queries:
            data = self.pending_request.execute_query(qry)
            if any(data):
                if 'results' in data['d']:
                    for item in data['d']['results']:
                        clientObject = ClientObject.create_typed_object(self, item)
                        qry.result_object.add_child(clientObject)
                else:
                    qry.result_object.properties = data['d']
            self.__queries.remove(qry)

    def add_query(self, query):
        self.__queries.append(query)

    @property
    def url(self):
        """Get base url"""
        return self.__base_url
