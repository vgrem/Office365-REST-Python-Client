import os

from office365.directory.extensions.extension import Extension
from office365.entity_collection import EntityCollection
from office365.outlook.item import OutlookItem
from office365.outlook.mail.attachments.collection import AttachmentCollection
from office365.outlook.mail.item_body import ItemBody
from office365.outlook.mail.recipient import Recipient
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery


class Message(OutlookItem):
    """A message in a mailbox folder."""

    def create_forward(self, to_recipients=None, message=None, comment=None):
        """
        Create a draft to forward an existing message, in either JSON or MIME format.

        :param list[Recipient] to_recipients:
        :param Message message:
        :param str comment:
        """
        return_type = Message(self.context)
        payload = {
            "ToRecipients": ClientValueCollection(Recipient, to_recipients),
            "Message": message,
            "Comment": comment
        }
        qry = ServiceOperationQuery(self, "createForward", None, payload, None, return_type)
        self.context.add_query(qry)
        return self

    def download(self, file_object):
        """Download MIME content of a message into a file

        :type file_object: typing.IO
        """
        def _save_content(return_type):
            """
            :type return_type: ClientResult
            """
            file_object.write(return_type.value)
        self.get_content().after_execute(_save_content)
        return self

    def get_content(self):
        """
        Get MIME content of a message
        """
        return_type = ClientResult(self.context)
        qry = FunctionQuery(self, "$value", None, return_type)
        self.context.add_query(qry)
        return return_type

    def add_file_attachment(
        self, name, content=None, content_type=None, base64_content=None):
        """
        Attach a file to message

        :param str name: The name representing the text that is displayed below the icon representing the
             embedded attachment
        :param str or None content: The contents of the file
        :param str or None content_type: The content type of the attachment.
        :param str or None base64_content: The contents of the file in the form of a base64 string.
        """
        if not content and not base64_content:
            raise TypeError("Either content or base64_content is required")
        self.attachments.add_file(name, content, content_type, base64_content)
        return self

    def upload_attachment(self, file_path, chunk_uploaded=None):
        """
        This approach is used to attach a file if the file size is between 3 MB and 150 MB, otherwise
        if a file that's smaller than 3 MB, then add_file_attachment method is utilized

        :param str file_path:
        :param ()->None chunk_uploaded: Upload action
        """
        max_upload_chunk = 1000000 * 3
        file_size = os.stat(file_path).st_size
        if file_size > max_upload_chunk:
            def _message_loaded():
                self.attachments.resumable_upload(file_path, max_upload_chunk, chunk_uploaded)
            self.ensure_property("id", _message_loaded)
        else:
            with open(file_path, 'rb') as file_object:
                content = file_object.read()
            self.attachments.add_file(os.path.basename(file_object.name), content.decode("utf-8"))
        return self

    def send(self):
        """
        Send a message in the draft folder. The draft message can be a new message draft, reply draft, reply-all draft,
        or a forward draft. The message is then saved in the Sent Items folder.
        """
        qry = ServiceOperationQuery(self, "send")
        self.context.add_query(qry)
        return self

    def reply(self, comment=None):
        """Reply to the sender of a message by specifying a comment and using the Reply method. The message is then
        saved in the Sent Items folder.

        :param str comment: A comment to include. Can be an empty string.
        """
        message = Message(self.context)
        payload = {
            "message": message,
            "comment": comment
        }
        qry = ServiceOperationQuery(self, "reply", None, payload)
        self.context.add_query(qry)
        return message

    def reply_all(self):
        """Reply to all recipients of a message. The message is then saved in the Sent Items folder. """
        qry = ServiceOperationQuery(self, "replyAll")
        self.context.add_query(qry)
        return self

    def create_reply(self, comment=None):
        """
        Create a draft to reply to the sender of a message in either JSON or MIME format.

        :param str comment:
        """
        return_type = Message(self.context)
        payload = {
            "comment": comment
        }
        qry = ServiceOperationQuery(self, "createReply", None, payload, None, return_type)
        self.context.add_query(qry)
        return self

    def create_reply_all(self):
        """
        Create a draft to reply to the sender and all the recipients of the specified message.
        You can then update the draft to add reply content to the body or change other message properties, or,
        simply send the draft.
        """
        qry = ServiceOperationQuery(self, "createReplyAll")
        self.context.add_query(qry)
        return self

    def move(self, destination_id):
        """
        Move a message to another folder within the specified user's mailbox.
        This creates a new copy of the message in the destination folder and removes the original message.

        :param str destination_id: The destination folder ID, or a well-known folder name.
            For a list of supported well-known folder names, see mailFolder resource type.
        """
        payload = {"DestinationId": destination_id}
        qry = ServiceOperationQuery(self, "move", None, payload, None, None)
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
        """The fileAttachment and itemAttachment attachments for the message.
        """
        self._persist_changes('attachments')
        return self.properties.setdefault('attachments',
                                          AttachmentCollection(self.context,
                                                               ResourcePath("attachments", self.resource_path)))

    @property
    def extensions(self):
        """The collection of open extensions defined for the message. Nullable."""
        return self.properties.get('extensions',
                                   EntityCollection(self.context, Extension,
                                                    ResourcePath("extensions", self.resource_path)))

    @property
    def body(self):
        """The body of the message. It can be in HTML or text format.

        :rtype: ItemBody
        """
        return self.properties.setdefault("body", ItemBody())

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
        self._persist_changes('toRecipients')
        return self.properties.setdefault('toRecipients', ClientValueCollection(Recipient))

    @property
    def bcc_recipients(self):
        """The BCC: recipients for the message."""
        self._persist_changes('bccRecipients')
        return self.properties.setdefault('bccRecipients', ClientValueCollection(Recipient))

    @property
    def cc_recipients(self):
        """The CC: recipients for the message."""
        self._persist_changes('ccRecipients')
        return self.properties.setdefault('ccRecipients', ClientValueCollection(Recipient))

    @property
    def sender(self):
        """The account that is actually used to generate the message. In most cases, this value is the same as the
        from property. You can set this property to a different value when sending a message from a shared mailbox,
        for a shared calendar, or as a delegate. In any case, the value must correspond to the actual mailbox used.
        Find out more about setting the from and sender properties of a message."""
        return self.properties.get('sender', Recipient())

    @property
    def parent_folder_id(self):
        """The unique identifier for the message's parent mailFolder.
        :rtype: str or None
        """
        return self.properties.get('parentFolderId', None)

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_type_mapping = {
                "toRecipients": self.to_recipients,
                "bccRecipients": self.bcc_recipients,
                "ccRecipients": self.cc_recipients
            }
            default_value = property_type_mapping.get(name, None)

        return super(Message, self).get_property(name, default_value)
