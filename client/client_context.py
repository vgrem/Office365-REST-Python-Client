from client.runtime.action_type import ActionType
from client.runtime.client_object import ClientObject
from client.runtime.client_query import ClientQuery
from client.runtime.client_request import ClientRequest
from site import Site
from web import Web


class ClientContext(object):
    """SharePoint client context"""

    def __init__(self, url, auth_context):
        self.__base_url = url
        self.__auth_context = auth_context
        self.__web = None
        self.__site = None
        self.__pending_request = None
        self.__queries = []
        self.__resultObjects = {}

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

    def load(self, client_object, properties_to_retrieve=[]):
        """Prepare query"""
        qry = ClientQuery(client_object.url, ActionType.ReadEntry)
        if qry not in self.__resultObjects:
            self.add_query(qry, client_object)

    def execute_query(self):
        """Submit pending request to the server"""
        for qry in self.__queries:
            data = self.pending_request.execute_query(qry)
            if any(data) and qry in self.__resultObjects:
                result_object = self.__resultObjects[qry]
                if 'results' in data['d']:
                    for item in data['d']['results']:
                        child_client_object = ClientObject.create_typed_object(self, item)
                        result_object.add_child(child_client_object)
                else:
                    result_object.from_json(data['d'])
            self.__queries.remove(qry)

    def add_query(self, query, result_object=None):
        self.__queries.append(query)
        if result_object is not None:
            self.__resultObjects[query] = result_object

    @property
    def url(self):
        """Get base url"""
        return self.__base_url
