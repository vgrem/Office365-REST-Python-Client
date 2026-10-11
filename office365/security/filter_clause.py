from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.security.filter_operand import FilterOperand


@dataclass
class FilterClause(ClientValue):
    operatorName: str | None = None
    sourceOperandName: str | None = None
    targetOperand: FilterOperand = field(default_factory=FilterOperand)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.FilterClause"
