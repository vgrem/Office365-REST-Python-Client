from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class AccessReviewContextDataBase(ClientValue):
    reviewDefinitionId: str | None = None
    reviewInstanceId: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.customDataProvidedResourcePayloads.AccessReviewContextDataBase"
