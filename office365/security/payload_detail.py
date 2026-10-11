from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.security.payload_coachmark import PayloadCoachmark


@dataclass
class PayloadDetail(ClientValue):
    coachmarks: ClientValueCollection[PayloadCoachmark] = field(
        default_factory=lambda: ClientValueCollection(PayloadCoachmark)
    )
    content: str | None = None
    phishingUrl: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PayloadDetail"
