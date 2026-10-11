from __future__ import annotations

from typing import List, Optional, Union

from office365.entity_collection import EntityCollection
from office365.runtime.queries.create_entity import CreateEntityQuery
from office365.runtime.queries.function import FunctionQuery
from office365.teams.chats.chat import Chat
from office365.teams.chats.messages.collection import ChatMessageCollection
from office365.teams.chats.type import ChatType


class ChatCollection(EntityCollection[Chat]):
    """Chat's collection"""

    def __init__(self, context, resource_path=None):
        super().__init__(context, Chat, resource_path)

    def add(
        self,
        chat_type: Union[str, ChatType],
        owner_ids: Optional[List[str]] = None,
        topic: Optional[str] = None,
    ) -> Chat:
        """Create a new chat object.

        Note: Only one one-on-one chat can exist between two members. If a one-on-one chat already exists,
        this operation will return the existing chat and not create a new one.

        Args:
            chat_type (str): Specifies the type of chat. Possible values are: group and oneOnOne.
            owner_ids (List[str]): The list of user IDs of the chat members that are owners.
            topic (str): The topic of the group chat (group chats only).
        """
        if isinstance(chat_type, ChatType):
            chat_type = chat_type.value

        initial_properties = {"chatType": chat_type}
        if topic:
            initial_properties["topic"] = topic
        return_type = self.create_typed_object(initial_properties)
        if owner_ids:
            from office365.teams.members.aad_user_conversation import (
                AadUserConversationMember,
            )

            for user_id in owner_ids:
                owner = AadUserConversationMember(self.context)
                owner.set_property("userId", user_id)
                owner.roles.add("owner")
                return_type.members.add_child(owner)
        self.add_child(return_type)
        qry = CreateEntityQuery(self, return_type, return_type)
        self.context.add_query(qry)
        return return_type

    def get_all_messages(self) -> ChatMessageCollection:
        """Export every chat message visible to the collection scope.

        Works for the tenant scope (``GET /chats/getAllMessages``) and a user's
        chats (``GET /users/{id}/chats/getAllMessages``). Application-only
        (``Teamwork.Migrate.All``). Deferred — run with ``execute_query()``.

        Chain ``.filter(...)``/``.select(...)``/``.top(...)`` on the returned
        collection to shape the request.
        """
        return_type = ChatMessageCollection(self.context, self.resource_path)
        qry = FunctionQuery(self, "getAllMessages", None, return_type)
        self.context.add_query(qry)
        return return_type
