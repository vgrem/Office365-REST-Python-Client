from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.types.collections import StringCollection
from office365.search.alteration_response import AlterationResponse
from office365.search.hits.container import SearchHitsContainer
from office365.search.result_template_dictionary import ResultTemplateDictionary


@dataclass
class SearchResponse(ClientValue):
    """Represents results from a search query, and the terms used for the query."""

    searchTerms: StringCollection = field(default_factory=StringCollection)
    hitsContainers: ClientValueCollection[SearchHitsContainer] = field(
        default_factory=lambda: ClientValueCollection(SearchHitsContainer)
    )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SearchResponse"

    queryAlterationResponse: AlterationResponse = field(default_factory=AlterationResponse)

    resultTemplates: ResultTemplateDictionary = field(default_factory=ResultTemplateDictionary)
