from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.webs.web_information import WebInformation


class WebInformationCollection(BaseEntityCollection):
    """Web Information collection"""

    def __init__(self, context, resource_path=None):
        super(WebInformationCollection, self).__init__(context, WebInformation, resource_path)
