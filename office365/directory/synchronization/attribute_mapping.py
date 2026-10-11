from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.synchronization.attributeflowbehavior import AttributeFlowBehavior
from office365.directory.synchronization.attributeflowtype import AttributeFlowType
from office365.runtime.client_value import ClientValue
from office365.security.attribute_mapping_source import AttributeMappingSource


@dataclass
class AttributeMapping(ClientValue):
    defaultValue: str | None = None
    exportMissingReferences: bool | None = None
    flowBehavior: AttributeFlowBehavior = AttributeFlowBehavior.FlowWhenChanged
    flowType: AttributeFlowType = AttributeFlowType.Always
    matchingPriority: int | None = None
    source: AttributeMappingSource = field(default_factory=AttributeMappingSource)
    targetAttributeName: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AttributeMapping"
