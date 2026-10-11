from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.communications.calls.eventtype import CallEventType
    from office365.communications.calls.participant import Participant


class CallEvent(Entity):
    @property
    def call_event_type(self) -> CallEventType:
        """Gets the callEventType property"""
        from office365.communications.calls.eventtype import CallEventType

        return self.properties.get("callEventType", CallEventType.callStarted)

    @property
    def event_date_time(self) -> Optional[datetime]:
        """Gets the eventDateTime property"""
        return self.properties.get("eventDateTime", datetime.min)

    @property
    def participants(self) -> EntityCollection[Participant]:
        """Gets the participants property"""
        from office365.communications.calls.participant import Participant

        return self.properties.get(
            "participants",
            EntityCollection[Participant](self.context, Participant, ResourcePath("participants", self.resource_path)),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CallEvent"
