from office365.runtime.action_type import ActionType
from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_query import ClientQuery
from office365.sharepoint.web import Web


class WebCollection(ClientObjectCollection):
    """Web collection"""
    def __init__(self, context, resource_path=None, parent_web_url=None):
        super(WebCollection, self).__init__(context, Web, resource_path)
        self._parent_web_url = parent_web_url

    def add(self, web_creation_information):
        web_creation_information._include_metadata = self.include_metadata
        payload = web_creation_information.payload
        web = Web(self.context)
        qry = ClientQuery(self.url + "/add", ActionType.PostMethod, payload)
        self.context.add_query(qry, web)
        self.add_child(web)
        return web

    @property
    def service_root_url(self):
        orig_root_url = super(WebCollection, self).service_root_url
        if self._parent_web_url:
            cur_root_url = self._parent_web_url + "/_api/"
            return cur_root_url
        return orig_root_url
