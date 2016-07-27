from client.runtime.client_object_collection import ClientObjectCollection
from client.runtime.client_query import ClientQuery
from client.runtime.action_type import ActionType


class WebCollection(ClientObjectCollection):
    """Web collection"""

    def add(self, web_creation_information):
        payload = web_creation_information.payload
        from web import Web
        web = Web(self.context)
        qry = ClientQuery(self.url + "/add", ActionType.UpdateMethod, payload)
        self.context.add_query(qry, web)
        self.add_child(web)
        return web
