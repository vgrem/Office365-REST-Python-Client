from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.security.filter_clause import FilterClause


@dataclass
class FilterGroup(ClientValue):
    clauses: ClientValueCollection[FilterClause] = field(default_factory=lambda: ClientValueCollection(FilterClause))
    name: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.FilterGroup"
