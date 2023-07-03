from office365.runtime.client_value import ClientValue


class ChatMessageAttachment(ClientValue):
    """
    Represents an attachment to a chat message entity.

    An entity of type chatMessageAttachment is returned as part of the Get channel messages API, as a part of
    chatMessage entity.
    """

    def __init__(self, content=None, content_type=None):
        """
        :param str content: The content of the attachment. If the attachment is a rich card, set the property to the
             rich card object. This property and contentUrl are mutually exclusive.
        :param str content_type: The media type of the content attachment. It can have the following values:
             reference: Attachment is a link to another file. Populate the contentURL with the link to the object.
             Any contentTypes supported by the Bot Framework's Attachment object
             application/vnd.microsoft.card.codesnippet: A code snippet.
             application/vnd.microsoft.card.announcement: An announcement header.
        """
        self.content = content
        self.contentType = content_type
