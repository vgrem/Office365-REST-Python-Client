from __future__ import annotations

from dataclasses import dataclass

from office365.directory.synchronization.attributedefinitionmetadata import AttributeDefinitionMetadata
from office365.runtime.client_value import ClientValue


@dataclass
class AttributeDefinitionMetadataEntry(ClientValue):
    key: AttributeDefinitionMetadata = AttributeDefinitionMetadata.BaseAttributeName
    value: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AttributeDefinitionMetadataEntry"
