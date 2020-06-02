from office365.graph.onedrive.contentType import ContentType
from office365.runtime.client_object_collection import ClientObjectCollection


class ContentTypeCollection(ClientObjectCollection):
    """Drive column's collection"""

    def __init__(self, context, resource_path=None):
        super(ContentTypeCollection, self).__init__(context, ContentType, resource_path)
