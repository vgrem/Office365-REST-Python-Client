from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from office365.entity_collection import EntityCollection
from office365.runtime.paths.v4.entity import EntityPath
from office365.runtime.queries.create_entity import CreateEntityQuery
from office365.runtime.types.collections import StringCollection
from office365.teams.members.aad_user_conversation import AadUserConversationMember
from office365.teams.members.conversation import ConversationMember

if TYPE_CHECKING:
    from office365.directory.users.user import User


class ConversationMemberCollection(EntityCollection[ConversationMember]):
    """ """

    def __init__(self, context, resource_path=None):
        super().__init__(context, ConversationMember, resource_path)

    def add(
        self,
        user: str | User,
        roles: list[str],
        visible_history_start_datetime: datetime | None = None,
    ):
        """Add a conversationMember.

        Graph only accepts the concrete ``#microsoft.graph.aadUserConversationMember``
        type together with a ``user@odata.bind`` reference for a team, channel or
        chat member — the generic ``conversationMember`` type is rejected — so an
        :class:`AadUserConversationMember` is created here.

        Args:
            user (str or office365.directory.users.user.User): The conversation member that should be added.
              Accepts a user id, a user principal name, or a ``User`` object.
            roles (list[str]): The roles for that user (``owner``, ``member`` or ``guest``).
            visible_history_start_datetime (datetime.datetime): When the member joined the conversation.
        """
        from office365.directory.users.user import User

        return_type = AadUserConversationMember(self.context, EntityPath(None, self.resource_path))
        self.add_child(return_type)
        return_type.set_property("roles", StringCollection(roles))
        if visible_history_start_datetime is not None:
            return_type.set_property("visibleHistoryStartDateTime", visible_history_start_datetime)

        if isinstance(user, User):
            user.ensure_property("id").after_execute(lambda _: return_type.set_property("userId", user.id))
        else:
            return_type.set_property("userId", user)

        qry = CreateEntityQuery(self, return_type, return_type)
        self.context.add_query(qry)
        return return_type
