from office365.graph.teams.chatMessage import ChatMessage
from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.queries.create_entity_query import CreateEntityQuery


class ChatMessageCollection(ClientObjectCollection):

    def __init__(self, context, resource_path=None):
        super(ChatMessageCollection, self).__init__(context, ChatMessage, resource_path)

    def add(self, item_body):
        """Create a new chatMessage in the specified channel.

        :param office365.graph.teams.itemBody.ItemBody item_body: Item body.
        """
        new_msg = ChatMessage(self.context)
        self.add_child(new_msg)
        payload = {
            "body": item_body,
        }
        qry = CreateEntityQuery(self, payload, new_msg)
        self.context.add_query(qry)
        return new_msg
