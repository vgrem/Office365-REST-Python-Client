from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.search.alterationtype import SearchAlterationType
from office365.search.search_alteration import SearchAlteration


@dataclass
class AlterationResponse(ClientValue):
    originalQueryString: str | None = None
    queryAlteration: SearchAlteration = field(default_factory=SearchAlteration)
    queryAlterationType: SearchAlterationType = SearchAlterationType.suggestion

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AlterationResponse"
