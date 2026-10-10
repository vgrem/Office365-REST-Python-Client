from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.search.altered_query_token import AlteredQueryToken


@dataclass
class SearchAlteration(ClientValue):
    alteredHighlightedQueryString: str | None = None
    alteredQueryString: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SearchAlteration"

    alteredQueryTokens: ClientValueCollection[AlteredQueryToken] = field(
        default_factory=lambda: ClientValueCollection(AlteredQueryToken)
    )
