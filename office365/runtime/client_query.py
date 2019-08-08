from office365.runtime.action_type import ActionType
from office365.runtime.odata.odata_path_parser import ODataPathParser


class ClientQuery(object):
    """Client query"""

    def __init__(self, url, action_type=ActionType.ReadEntity, payload=None):
        self.__url = url
        self.__actionType = action_type
        self.__payload = payload

    @staticmethod
    def read_entry_query(client_object):
        qry = ClientQuery(client_object.resource_url, ActionType.ReadEntity)
        return qry

    @staticmethod
    def create_entry_query(parent_client_object, parameters):
        qry = ClientQuery(parent_client_object.resource_url, ActionType.CreateEntity, parameters)
        return qry

    @staticmethod
    def update_entry_query(client_object):
        qry = ClientQuery(client_object.resource_url, ActionType.UpdateEntity, client_object)
        return qry

    @staticmethod
    def delete_entry_query(client_object):
        qry = ClientQuery(client_object.resource_url, ActionType.DeleteEntity)
        return qry

    @staticmethod
    def service_operation_query(client_object, action_type, method_name, method_params=None, payload=None):
        url = client_object.resource_url + "/" + ODataPathParser.from_method(method_name, method_params)
        qry = ClientQuery(url, action_type, payload)
        return qry

    @property
    def url(self):
        return self.__url

    @property
    def action_type(self):
        return self.__actionType

    @property
    def payload(self):
        return self.__payload

    @property
    def id(self):
        return id(self)

    def execute(self, context, client_object=None):
        from office365.runtime.client_request import ClientRequest
        return ClientRequest(context).execute_single_query(self, client_object)

    def __hash__(self):
        return hash(self.url)

    def __eq__(self, other):
        return self.url == other.url
