from __future__ import annotations

from dataclasses import dataclass, field

from office365.externalconnectors.binaryoperator import BinaryOperator
from office365.externalconnectors.rule_operation import RuleOperation
from office365.runtime.client_value import ClientValue
from office365.runtime.types.collections import StringCollection


@dataclass
class PropertyRule(ClientValue):
    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.externalConnectors.PropertyRule"

    property: str | None = None
    values: StringCollection = field(default_factory=StringCollection)

    operation: RuleOperation = RuleOperation.null

    valuesJoinedBy: BinaryOperator = BinaryOperator.or_
