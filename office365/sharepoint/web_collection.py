from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_query import ServiceOperationQuery
from office365.sharepoint.web import Web


class WebCollection(ClientObjectCollection):
    """Web collection"""
    def __init__(self, context, resource_path=None, parent_web_url=None):
        super(WebCollection, self).__init__(context, Web, resource_path)
        self._parent_web_url = parent_web_url

    def add(self, web_creation_information):
        web = Web(self.context)
        qry = ServiceOperationQuery(self, "add", None, web_creation_information)
        self.context.add_query(qry, web)
        self.add_child(web)
        return web

    @property
    def resourceUrl(self):
        url = super(WebCollection, self).resourceUrl
        if self._parent_web_url is not None:
            url = url.replace(self.context.serviceRootUrl, self._parent_web_url + '/_api/')
        return url

