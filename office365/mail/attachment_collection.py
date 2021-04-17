from office365.entity_collection import EntityCollection
from office365.mail.attachment import Attachment


class AttachmentCollection(EntityCollection):
    """Attachment collection"""

    def __init__(self, context, resource_path=None):
        super(AttachmentCollection, self).__init__(context, Attachment, resource_path)
