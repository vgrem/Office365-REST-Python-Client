from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.serviceOperationQuery import ServiceOperationQuery
from office365.sharepoint.web import Web


class WebCollection(ClientObjectCollection):
    """Web collection"""

    def __init__(self, context, resource_path=None, parent_web_url=None):
        super(WebCollection, self).__init__(context, Web, resource_path)
        self._parent_web_url = parent_web_url

    def add(self, web_creation_information):
        target_web = Web(self.context)
        self.add_child(target_web)
        qry = ServiceOperationQuery(self, "add", None, web_creation_information, "parameters", target_web)
        self.context.add_query(qry)
        return target_web

    @property
    def resource_url(self):
        url = super(WebCollection, self).resource_url
        if self._parent_web_url is not None:
            url = url.replace(self.context.service_root_url, self._parent_web_url + '/_api/')
        return url
