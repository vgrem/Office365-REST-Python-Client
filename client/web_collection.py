from client.runtime.client_query import ClientQuery
from client_object_collection import ClientObjectCollection


class WebCollection(ClientObjectCollection):
    """Web collection"""

    def add(self, web_creation_information):
        payload = web_creation_information.metadata
        from web import Web
        web = Web(self.context)
        qry = ClientQuery.create_create_query(self.url + "/add", payload)
        self.context.add_query(qry, web)
        self.add_child(web)
        return web
