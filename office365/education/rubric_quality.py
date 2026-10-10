from __future__ import annotations

from dataclasses import dataclass, field

from office365.education.rubric_criterion import RubricCriterion
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


@dataclass
class RubricQuality(ClientValue):
    criteria: ClientValueCollection[RubricCriterion] = field(
        default_factory=lambda: ClientValueCollection(RubricCriterion)
    )
    displayName: str | None = None
    qualityId: str | None = None
    weight: float | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.RubricQuality"
