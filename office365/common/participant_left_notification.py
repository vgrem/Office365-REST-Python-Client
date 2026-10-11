from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.communications.calls.call import Call


class ParticipantLeftNotification(Entity):
    @property
    def participant_id(self) -> Optional[str]:
        """Gets the participantId property"""
        return self.properties.get("participantId", None)

    @property
    def call(self) -> Call:
        """Gets the call property"""
        from office365.communications.calls.call import Call

        return self.properties.get("call", Call(self.context, ResourcePath("call", self.resource_path)))

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ParticipantLeftNotification"
