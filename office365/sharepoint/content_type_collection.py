from office365.runtime.client_object_collection import ClientObjectCollection
from office365.sharepoint.content_type import ContentType

class ContentTypeCollection(ClientObjectCollection):
    """Content Type resource collection"""

    # The object type this collection holds
    item_type = ContentType
