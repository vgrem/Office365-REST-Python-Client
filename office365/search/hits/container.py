from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.search.aggregation import SearchAggregation
from office365.search.hits.hit import SearchHit


@dataclass
class SearchHitsContainer(ClientValue):
    """Represent the list of search results."""

    hits: ClientValueCollection[SearchHit] = field(default_factory=lambda: ClientValueCollection(SearchHit))
    moreResultsAvailable: bool | None = None
    total: int | None = None
    aggregations: ClientValueCollection[SearchAggregation] = field(
        default_factory=lambda: ClientValueCollection(SearchAggregation)
    )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SearchHitsContainer"
