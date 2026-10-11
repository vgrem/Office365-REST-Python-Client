from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.communications.callrecords.session import Session
from office365.communications.callrecords.type import CallType
from office365.communications.calls.organizer import Organizer
from office365.communications.calls.participant import Participant
from office365.directory.permissions.identity_set import IdentitySet
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.limits import Limit, LimitKind, limit
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.communications.callrecords.modality import Modality

_DOC = "https://learn.microsoft.com/en-us/graph/throttling-limits"


@limit(
    Limit("call records", 15_000, LimitKind.SUPPORTED, "requests", "app", doc=_DOC, window_seconds=20),
    Limit("call records", 10_000, LimitKind.SUPPORTED, "requests", "tenant", doc=_DOC, window_seconds=20),
    Limit("call records", 1_500, LimitKind.SUPPORTED, "requests", "app+tenant", doc=_DOC, window_seconds=20),
    Limit(
        "call records",
        40,
        LimitKind.SUPPORTED,
        "requests",
        "resource",
        note="per call record",
        doc=_DOC,
        window_seconds=20,
    ),
)
class CallRecord(Entity):
    """Represents a single peer-to-peer call or a group call between multiple participants,
    sometimes referred to as an online meeting."""

    @property
    def join_web_url(self) -> Optional[str]:
        """Meeting URL associated to the call. May not be available for a peerToPeer call record type."""
        return self.properties.get("joinWebUrl", None)

    @property
    def organizer(self) -> IdentitySet:
        """The organizing party's identity.."""
        return self.properties.get("organizer", IdentitySet())

    @property
    def sessions(self) -> EntityCollection[Session]:
        """
        List of sessions involved in the call. Peer-to-peer calls typically only have one session, whereas group
        calls typically have at least one session per participant.
        """
        return self.properties.get(
            "sessions", EntityCollection(self.context, Session, ResourcePath("sessions", self.resource_path))
        )

    @property
    def end_date_time(self) -> datetime:
        """Gets the endDateTime property"""
        return self.properties.get("endDateTime", datetime.min)

    @property
    def last_modified_date_time(self) -> datetime:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def participants(self) -> ClientValueCollection[IdentitySet]:
        """Gets the participants property"""
        return self.properties.get("participants", ClientValueCollection[IdentitySet](IdentitySet))

    @property
    def start_date_time(self) -> datetime:
        """Gets the startDateTime property"""
        return self.properties.get("startDateTime", datetime.min)

    @property
    def type_(self) -> CallType:
        """Gets the type property"""
        return self.properties.get("type", CallType.unknown)

    @property
    def version(self) -> Optional[int]:
        """Gets the version property"""
        return self.properties.get("version", None)

    @property
    def organizer_v2(self) -> Organizer:
        """Gets the organizer_v2 property"""
        return self.properties.get(
            "organizer_v2", Organizer(self.context, ResourcePath("organizer_v2", self.resource_path))
        )

    @property
    def participants_v2(self) -> EntityCollection[Participant]:
        """Gets the participants_v2 property"""
        return self.properties.get(
            "participants_v2",
            EntityCollection[Participant](
                self.context, Participant, ResourcePath("participants_v2", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.callRecords.CallRecord"

    @property
    def modalities(self) -> ClientValueCollection[Modality]:
        """Gets the modalities property"""
        from office365.communications.callrecords.modality import Modality

        return self.properties.get("modalities", ClientValueCollection[Modality](Modality))
