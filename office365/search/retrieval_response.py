from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.search.retrieval_hit import RetrievalHit


@dataclass
class RetrievalResponse(ClientValue):
    retrievalHits: ClientValueCollection[RetrievalHit] = field(
        default_factory=lambda: ClientValueCollection(RetrievalHit)
    )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.RetrievalResponse"
