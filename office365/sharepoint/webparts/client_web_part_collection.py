from office365.runtime.client_object_collection import ClientObjectCollection
from office365.sharepoint.webparts.client_web_part import ClientWebPart


class ClientWebPartCollection(ClientObjectCollection):
    """Web collection"""

    def __init__(self, context, resource_path=None):
        super(ClientWebPartCollection, self).__init__(context, ClientWebPart, resource_path)
