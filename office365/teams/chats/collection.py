from office365.entity_collection import EntityCollection
from office365.teams.chats.chat import Chat


class ChatCollection(EntityCollection):
    """Team's collection"""

    def __init__(self, context, resource_path=None):
        super(ChatCollection, self).__init__(context, Chat, resource_path)

    def add(self, chat_type, members):
        """
        Create a new chat object.

        Note: Only one one-on-one chat can exist between two members. If a one-on-one chat already exists,
        this operation will return the existing chat and not create a new one.

        :param str chat_type: Specifies the type of chat. Possible values are: group and oneOnOne.
        :param list[] members: List of conversation members that should be added. Every user who will participate
            in the chat, including the user who initiates the create request, must be specified in this list.
            Each member must be assigned a role of owner or guest. Guest tenant members must be assigned the guest role
        """
        return super(ChatCollection, self).add(chatType=chat_type, members=members)


