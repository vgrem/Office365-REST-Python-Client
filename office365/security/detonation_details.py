from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.security.compromise_indicator import CompromiseIndicator
from office365.security.detonation_behaviour_details import DetonationBehaviourDetails
from office365.security.detonation_chain import DetonationChain
from office365.security.detonation_observables import DetonationObservables


@dataclass
class DetonationDetails(ClientValue):
    analysisDateTime: datetime | None = field(default_factory=lambda: datetime.min)
    detonationBehaviourDetailsV2: str | None = None
    detonationScreenshotUri: str | None = None
    detonationVerdict: str | None = None
    detonationVerdictReason: str | None = None
    entityMetadata: str | None = None
    mitreTechniques: str | None = None
    staticAnalysis: str | None = None
    submissionSource: str | None = None
    compromiseIndicators: ClientValueCollection[CompromiseIndicator] = field(
        default_factory=lambda: ClientValueCollection(CompromiseIndicator)
    )
    detonationBehaviourDetails: DetonationBehaviourDetails = field(default_factory=DetonationBehaviourDetails)
    detonationChain: DetonationChain = field(default_factory=DetonationChain)
    detonationObservables: DetonationObservables = field(default_factory=DetonationObservables)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.DetonationDetails"
