from office365.runtime.client_value import ClientValue


class AttachmentItem(ClientValue):
    """Represents attributes of an item to be attached."""

    def __init__(self, attachment_type, name, size):
        super(AttachmentItem, self).__init__()
        self.attachmentType = attachment_type
        self.name = name
        self.size = size
