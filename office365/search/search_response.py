from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.types.collections import StringCollection
from office365.search.search_hits_container import SearchHitsContainer


@dataclass
class SearchResponse(ClientValue):
    hitsContainers: ClientValueCollection[SearchHitsContainer] = field(
        default_factory=lambda: ClientValueCollection(SearchHitsContainer)
    )
    searchTerms: StringCollection = field(default_factory=StringCollection)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SearchResponse"
