from office365.directory.extensions.extension import Extension
from office365.entity_collection import EntityCollection
from office365.outlook.mail.attachments.attachment_collection import AttachmentCollection
from office365.outlook.mail.attachments.attachment_type import AttachmentType
from office365.outlook.mail.attachments.file_attachment import FileAttachment
from office365.outlook.mail.attachments.item_attachment import ItemAttachment
from office365.outlook.mail.attachments.reference_attachment import ReferenceAttachment
from office365.outlook.mail.item import Item
from office365.outlook.mail.itemBody import ItemBody
from office365.outlook.mail.recipient import Recipient
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.resource_path import ResourcePath


class Message(Item):
    """A message in a mailbox folder."""

    def add_attachment(self, attachment_type=AttachmentType.file):
        attachment_known_types = {
            AttachmentType.file: FileAttachment,
            AttachmentType.item: ItemAttachment,
            AttachmentType.reference: ReferenceAttachment,
        }
        attachment = attachment_known_types.get(attachment_type)(self.context)
        self.attachments.add_child(attachment)
        self.set_property('attachments', attachment.parent_collection, True)
        return attachment

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

    @property
    def extensions(self):
        """The collection of open extensions defined for the message. Nullable."""
        return self.properties.get('extensions',
                                   EntityCollection(self.context, Extension,
                                                    ResourcePath("extensions", self.resource_path)))

    @property
    def body(self):
        """The body of the message. It can be in HTML or text format."""
        return self.get_property("body", ItemBody())

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

        :type value: list[str] or list[Recipient]
        """
        self.set_property('toRecipients',
                          ClientValueCollection(Recipient, [Recipient.from_email(email) for email in value]))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_type_mapping = {
                "toRecipients": self.to_recipients
            }
            default_value = property_type_mapping.get(name, None)
        return super(Message, self).get_property(name, default_value)
