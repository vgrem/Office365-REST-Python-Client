from office365.entity_collection import EntityCollection
from office365.onedrive.contentType import ContentType


class ContentTypeCollection(EntityCollection):
    """Content Type's collection"""

    def __init__(self, context, resource_path=None):
        super(ContentTypeCollection, self).__init__(context, ContentType, resource_path)
