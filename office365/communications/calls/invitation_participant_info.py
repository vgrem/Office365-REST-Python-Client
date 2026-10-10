from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.permissions.identity_set import IdentitySet
from office365.runtime.client_value import ClientValue


@dataclass
class InvitationParticipantInfo(ClientValue):
    """This resource is used to represent the entity that is being invited to a group call.

    Fields:
        hidden: Optional. Whether to hide the participant from the roster.
        identity: The identitySet associated with this invitation.
        participantId: Optional. The ID of the target participant.
        removeFromDefaultAudioRoutingGroup: Optional. Whether to remove them from the main mixer.
        replacesCallId: Optional. The call which the target identity is currently a part of.
            For peer-to-peer case, the call will be dropped once the participant is added successfully.
    """

    hidden: bool | None = None
    identity: IdentitySet = field(default_factory=IdentitySet)
    participantId: str | None = None
    removeFromDefaultAudioRoutingGroup: bool | None = None
    replacesCallId: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.InvitationParticipantInfo"
