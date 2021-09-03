from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.webparts.client_web_part import ClientWebPart


class ClientWebPartCollection(BaseEntityCollection):
    """Web collection"""

    def __init__(self, context, resource_path=None):
        super(ClientWebPartCollection, self).__init__(context, ClientWebPart, resource_path)

    def get_by_id(self, _id):
        """Gets the Client web part with the specified ID."""
        return ClientWebPart(self.context, ResourcePathServiceOperation("getById", [_id], self.resource_path))
