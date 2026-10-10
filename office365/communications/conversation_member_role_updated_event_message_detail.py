from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.identity_set import IdentitySet
from office365.runtime.client_value import ClientValue
from office365.runtime.types.collections import StringCollection
from office365.teams.teamwork.user_identity import TeamworkUserIdentity


@dataclass
class ConversationMemberRoleUpdatedEventMessageDetail(ClientValue):
    conversationMemberRoles: StringCollection = field(default_factory=StringCollection)
    conversationMemberUser: TeamworkUserIdentity = field(default_factory=TeamworkUserIdentity)
    initiator: IdentitySet = field(default_factory=IdentitySet)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ConversationMemberRoleUpdatedEventMessageDetail"
