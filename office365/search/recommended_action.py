from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class RecommendedAction(ClientValue):
    actionWebUrl: str | None = None
    potentialScoreImpact: float | None = None
    title: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.RecommendedAction"
