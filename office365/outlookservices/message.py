from office365.outlookservices.item import Item
from office365.runtime.action_type import ActionType
from office365.runtime.client_query import ClientQuery


class Message(Item):
    """A message in a mailbox folder."""

    def reply(self):
        """Reply to the sender of a message by specifying a comment and using the Reply method. The message is then
        saved in the Sent Items folder. """
        qry = ClientQuery.service_operation_query(self,
                                                  ActionType.PostMethod,
                                                  "reply",
                                                  )
        self.context.add_query(qry)

    def move(self):
        """Move a message to a folder. This creates a new copy of the message in the destination folder. """
        qry = ClientQuery.service_operation_query(self,
                                                  ActionType.PostMethod,
                                                  "move",
                                                  )
        self.context.add_query(qry)
