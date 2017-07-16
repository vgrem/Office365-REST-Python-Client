from office365.runtime.action_type import ActionType
from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_query import ClientQuery


class WebCollection(ClientObjectCollection):
    """Web collection"""

    def add(self, web_creation_information):
        web_creation_information._include_metadata = self.include_metadata
        payload = web_creation_information.payload
        from office365.sharepoint.web import Web
        web = Web(self.context)
        qry = ClientQuery(self.url + "/add", ActionType.PostMethod, payload)
        self.context.add_query(qry, web)
        self.add_child(web)
        return web
