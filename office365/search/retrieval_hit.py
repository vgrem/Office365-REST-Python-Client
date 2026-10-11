from __future__ import annotations

from dataclasses import dataclass, field

from office365.copilot.retrieval_entity_type import RetrievalEntityType
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.search.retrieval_extract import RetrievalExtract
from office365.search.search_resource_metadata_dictionary import (
    SearchResourceMetadataDictionary,
)
from office365.security.sensitivity_label_info import SensitivityLabelInfo


@dataclass
class RetrievalHit(ClientValue):
    extracts: ClientValueCollection[RetrievalExtract] = field(
        default_factory=lambda: ClientValueCollection(RetrievalExtract)
    )
    resourceMetadata: SearchResourceMetadataDictionary = field(default_factory=SearchResourceMetadataDictionary)
    resourceType: RetrievalEntityType = RetrievalEntityType.site
    sensitivityLabel: SensitivityLabelInfo = field(default_factory=SensitivityLabelInfo)
    webUrl: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.RetrievalHit"
