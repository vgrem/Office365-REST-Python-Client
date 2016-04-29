from client.runtime.client_action_type import ClientActionType


class ClientQuery(object):
    """Client query"""

    def __init__(self, url, action_type=ClientActionType.Read, parameters=None):
        self.__resultObject = None
        self.__url = url
        self.__actionType = action_type
        self.__parameters = parameters

    def add_result_object(self, client_object):
        self.__resultObject = client_object

    @staticmethod
    def create_create_query(client_object, url, parameters):
        qry = ClientQuery(url, ClientActionType.Create, parameters)
        qry.add_result_object(client_object)
        return qry

    @staticmethod
    def create_update_query(client_object, parameters):
        qry = ClientQuery(client_object.url, ClientActionType.Update, parameters)
        return qry

    @staticmethod
    def create_delete_query(client_object, url=None):
        if url:
            qry = ClientQuery(url, ClientActionType.Delete)
        else:
            qry = ClientQuery(client_object.url, ClientActionType.Delete)
        return qry

    @property
    def url(self):
        return self.__url

    @property
    def action_type(self):
        return self.__actionType

    @property
    def parameters(self):
        return self.__parameters

    @property
    def result_object(self):
        return self.__resultObject
