from office365.mail.item import Item
from office365.runtime.queries.service_operation_query import ServiceOperationQuery


class Message(Item):
    """A message in a mailbox folder."""

    def reply(self):
        """Reply to the sender of a message by specifying a comment and using the Reply method. The message is then
        saved in the Sent Items folder. """
        qry = ServiceOperationQuery(self, "reply")
        self.context.add_query(qry)
        return self

    def move(self):
        """Move a message to a folder. This creates a new copy of the message in the destination folder. """
        qry = ServiceOperationQuery(self, "move")
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
