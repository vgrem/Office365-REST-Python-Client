from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.webs.web import Web


class WebCollection(BaseEntityCollection):
    """Web collection"""

    def __init__(self, context, resource_path=None, parent_web=None):
        """
        :type parent_web: Web
        """
        super(WebCollection, self).__init__(context, Web, resource_path, parent_web)

    def add(self, web_creation_information):
        """
        Create WebSite

        :type web_creation_information: office365.sharepoint.webs.creation_information.WebCreationInformation
        """
        return_type = Web(self.context)
        self.add_child(return_type)
        payload = {"parameters": web_creation_information}
        qry = ServiceOperationQuery(self, "add", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def resource_url(self):
        val = super(WebCollection, self).resource_url
        parent_web_url = self._parent.get_property("Url")
        if parent_web_url is not None:
            val = val.replace(self.context.service_root_url(), parent_web_url + '/_api')
        return val
