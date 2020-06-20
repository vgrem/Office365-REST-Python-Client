from office365.runtime.client_object_collection import ClientObjectCollection
from office365.sharepoint.contenttypes.content_type import ContentType


class ContentTypeCollection(ClientObjectCollection):
    """Content Type resource collection"""
    def __init__(self, context, resource_path=None):
        super(ContentTypeCollection, self).__init__(context, ContentType, resource_path)
