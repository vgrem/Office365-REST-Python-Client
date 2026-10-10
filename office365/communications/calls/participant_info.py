from __future__ import annotations

from dataclasses import dataclass, field

from office365.communications.endpointtype import EndpointType
from office365.directory.permissions.identity_set import IdentitySet
from office365.runtime.client_value import ClientValue


@dataclass
class ParticipantInfo(ClientValue):
    """Contains additional properties about the participant identity

    Fields:
        countryCode: The ISO 3166-1 Alpha-2 country code of the participant's best estimated physical
            location at the start of the call.
    """

    countryCode: str | None = None

    endpointType: EndpointType = EndpointType.default

    identity: IdentitySet = field(default_factory=IdentitySet)

    languageId: str | None = None

    participantId: str | None = None

    region: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ParticipantInfo"
