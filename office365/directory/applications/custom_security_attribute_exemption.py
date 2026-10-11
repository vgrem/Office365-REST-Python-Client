from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue
from office365.security.custom_security_attribute_comparison_operator import (
    CustomSecurityAttributeComparisonOperator,
)


@dataclass
class CustomSecurityAttributeExemption(ClientValue):
    id: str | None = None
    operator: CustomSecurityAttributeComparisonOperator = CustomSecurityAttributeComparisonOperator.equals

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CustomSecurityAttributeExemption"
