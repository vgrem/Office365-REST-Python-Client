from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.search.search_aggregation import SearchAggregation
from office365.search.search_hit import SearchHit


@dataclass
class SearchHitsContainer(ClientValue):
    moreResultsAvailable: bool | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SearchHitsContainer"

    aggregations: ClientValueCollection[SearchAggregation] = field(
        default_factory=lambda: ClientValueCollection(SearchAggregation)
    )

    hits: ClientValueCollection[SearchHit] = field(default_factory=lambda: ClientValueCollection(SearchHit))

    total: int | None = None
