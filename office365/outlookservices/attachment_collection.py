from office365.runtime.client_object_collection import ClientObjectCollection
from office365.outlookservices.attachment import Attachment


class AttachmentCollection(ClientObjectCollection):
    """Attachment collection"""

    # The object type this collection holds
    item_type = Attachment
