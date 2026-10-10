from __future__ import annotations

from dataclasses import dataclass

from office365.directory.policies.match_confidence_level import MatchConfidenceLevel
from office365.runtime.client_value import ClientValue


@dataclass
class ClaimBinding(ClientValue):
    matchConfidenceLevel: MatchConfidenceLevel = MatchConfidenceLevel.exact
    sourceAttribute: str | None = None
    verifiedIdClaim: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ClaimBinding"
