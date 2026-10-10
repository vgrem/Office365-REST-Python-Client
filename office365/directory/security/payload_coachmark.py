from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.security.coachmark_location import CoachmarkLocation
from office365.runtime.client_value import ClientValue


@dataclass
class PayloadCoachmark(ClientValue):
    description: str | None = None
    indicator: str | None = None
    isValid: bool | None = None
    language: str | None = None
    order: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PayloadCoachmark"

    coachmarkLocation: CoachmarkLocation = field(default_factory=CoachmarkLocation)
