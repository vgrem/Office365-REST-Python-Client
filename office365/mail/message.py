from office365.directory.extension import ExtensionCollection
from office365.mail.attachment_collection import AttachmentCollection
from office365.mail.item import Item
from office365.mail.itemBody import ItemBody
from office365.mail.recipient import Recipient
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.resource_path import ResourcePath


class Message(Item):
    """A message in a mailbox folder."""

    def send(self):
        """
        Send a message in the draft folder. The draft message can be a new message draft, reply draft, reply-all draft,
        or a forward draft. The message is then saved in the Sent Items folder.
        """
        qry = ServiceOperationQuery(self, "send")
        self.context.add_query(qry)
        return self

    def reply(self):
        """Reply to the sender of a message by specifying a comment and using the Reply method. The message is then
        saved in the Sent Items folder. """
        qry = ServiceOperationQuery(self, "reply")
        self.context.add_query(qry)
        return self

    def reply_all(self):
        """Reply to all recipients of a message. The message is then saved in the Sent Items folder. """
        qry = ServiceOperationQuery(self, "replyAll")
        self.context.add_query(qry)
        return self

    def create_reply_all(self):
        """
        Create a draft to reply to the sender and all the recipients of the specified message.
        You can then update the draft to add reply content to the body or change other message properties, or,
        simply send the draft.
        :return:
        """
        qry = ServiceOperationQuery(self, "createReplyAll")
        self.context.add_query(qry)
        return self

    def move(self):
        """
        Move a message to another folder within the specified user's mailbox.
        This creates a new copy of the message in the destination folder and removes the original message.
        """
        qry = ServiceOperationQuery(self, "move")
        self.context.add_query(qry)
        return self

    def forward(self, to_recipients, comment=""):
        """
        Forward a message. The message is saved in the Sent Items folder.
        :param list[str] to_recipients: The list of recipients.
        :param str comment: A comment to include. Can be an empty string.
        """
        payload = {
            "toRecipients": ClientValueCollection(Recipient,
                                                  [Recipient.from_email(v) for v in to_recipients]),
            "comment": comment
        }
        qry = ServiceOperationQuery(self, "forward", None, payload)
        self.context.add_query(qry)
        return self

    @property
    def has_attachments(self):
        """
        Indicates whether the message has attachments. This property doesn't include inline attachments,
        so if a message contains only inline attachments, this property is false. To verify the existence
        of inline attachments, parse the body property to look for a src attribute,
        such as <IMG src="cid:image001.jpg@01D26CD8.6C05F070">.

        :rtype: bool or None
        """
        return self.properties.get("hasAttachments", None)

    @property
    def attachments(self):
        """The fileAttachment and itemAttachment attachments for the message."""
        return self.properties.get('attachments',
                                   AttachmentCollection(self.context, ResourcePath("attachments", self.resource_path)))

    @attachments.setter
    def attachments(self, value):
        """
        Sets the fileAttachment and itemAttachment attachments for the message.
        :type value list[office365.mail.attachment.Attachment]
        """
        col = AttachmentCollection(self.context, ResourcePath("attachments", self.resource_path))
        [col.add_child(item) for item in value]
        self.set_property('attachments', col)

    @property
    def extensions(self):
        """The collection of open extensions defined for the message. Nullable."""
        return self.properties.get('extensions',
                                   ExtensionCollection(self.context, ResourcePath("extensions", self.resource_path)))

    @property
    def body(self):
        """The body of the message. It can be in HTML or text format."""
        return self.properties.get("body", ItemBody())

    @body.setter
    def body(self, value):
        """The body of the message. It can be in HTML or text format.

        :type value: str or ItemBody
        """
        if not isinstance(value, ItemBody):
            value = ItemBody(value)
        self.set_property("body", value)

    @property
    def subject(self):
        """The subject of the message."""
        return self.properties.get("subject", None)

    @subject.setter
    def subject(self, value):
        """The subject of the message.

        :type value: str
        """
        self.set_property("subject", value)

    @property
    def to_recipients(self):
        """The To: recipients for the message."""
        return self.properties.get('toRecipients', ClientValueCollection(Recipient))

    @to_recipients.setter
    def to_recipients(self, value):
        """
        The To: recipients for the message.
        :type value: list[str]
        """
        self.set_property('toRecipients',
                          ClientValueCollection(Recipient, [Recipient.from_email(email) for email in value]))
