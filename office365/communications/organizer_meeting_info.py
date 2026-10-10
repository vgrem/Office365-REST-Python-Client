from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.identity_set import IdentitySet
from office365.runtime.client_value import ClientValue


@dataclass
class OrganizerMeetingInfo(ClientValue):
    organizer: IdentitySet = field(default_factory=IdentitySet)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.OrganizerMeetingInfo"
