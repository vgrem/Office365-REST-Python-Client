from office365.outlookservices.item import Item
from office365.runtime.client_query import ClientQuery, ServiceOperationQuery
from office365.runtime.utilities.http_method import HttpMethod


class Message(Item):
    """A message in a mailbox folder."""

    def reply(self):
        """Reply to the sender of a message by specifying a comment and using the Reply method. The message is then
        saved in the Sent Items folder. """
        qry = ServiceOperationQuery(self,
                                    HttpMethod.Post,
                                    "reply",
                                    )
        self.context.add_query(qry)

    def move(self):
        """Move a message to a folder. This creates a new copy of the message in the destination folder. """
        qry = ServiceOperationQuery(self,
                                    HttpMethod.Post,
                                    "move",
                                    )
        self.context.add_query(qry)
