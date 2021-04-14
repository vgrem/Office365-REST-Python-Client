from office365.runtime.client_object_collection import ClientObjectCollection
from office365.sharepoint.webs.web_information import WebInformation


class WebInformationCollection(ClientObjectCollection):
    """Web Information collection"""

    def __init__(self, context, resource_path=None):
        super(WebInformationCollection, self).__init__(context, WebInformation, resource_path)
