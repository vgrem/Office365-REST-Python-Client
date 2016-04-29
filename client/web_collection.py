from client_object_collection import ClientObjectCollection
from client.runtime.client_query import ClientQuery


class WebCollection(ClientObjectCollection):
    """Web collection"""

    def add(self, web_creation_information):
        payload = {'parameters': {'__metadata': {'type': 'SP.WebCreationInformation'}}}
        for key in web_creation_information:
            payload['parameters'][key] = web_creation_information[key]
        from web import Web
        web = Web(self.context)
        qry = ClientQuery.create_create_query(web, self.url + "/add", payload)
        self.context.add_query(qry)
        self.add_child(web)
        return web
